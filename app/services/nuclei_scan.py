# app/services/nuclei_scan.py

import asyncio
import json
from typing import Dict, List, Any, Optional

from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.scan import ScanStatus

logger = get_logger(__name__)

# Constants
BUFFER_SPLIT_RATIO = 2  # Keep 1/2 of buffer when overflow occurs
LOCALHOST_RATE_LIMIT = 200  # Higher rate limit for localhost scans
ERROR_RATE_THRESHOLD = 0.2  # 20% error rate triggers partial status
MAX_ERROR_LOGS = 5  # Maximum number of parse errors to log


class NucleiScanner:
    """
    Async Nuclei scanner with memory safety and buffer management.
    """
    
    def __init__(
        self,
        timeout: Optional[int] = None,
        rate_limit: Optional[int] = None,
        severity_filter: Optional[List[str]] = None,
        template_path: Optional[str] = None
    ):
        self.timeout = timeout or settings.NUCLEI_TIMEOUT
        self.rate_limit = rate_limit or settings.NUCLEI_RATE_LIMIT
        self.chunk_size = settings.NUCLEI_BUFFER_SIZE
        self.max_buffer_size = settings.MAX_BUFFER_SIZE
        self.max_vulnerabilities = settings.MAX_VULNERABILITIES
        self.severity_filter = severity_filter
        self.template_path = template_path
    
    async def scan(self, target: str) -> Dict[str, Any]:
        """
        Execute Nuclei vulnerability scan.
        
        Args:
            target: Full URL with scheme (http:// or https://)
        
        Returns:
            Scan results dictionary
        """
        
        logger.info(f"Starting Nuclei scan: {target}", extra={"target": target})
        
        # Optimize for localhost
        if "127.0.0.1" in target or "localhost" in target:
            self.rate_limit = LOCALHOST_RATE_LIMIT
            logger.debug("Using higher rate limit for localhost")
        
        command = self._build_command(target)
        
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except FileNotFoundError:
            logger.error("Nuclei not installed on system")
            return {
                "status": ScanStatus.FAILED.value,
                "error": "Nuclei not installed",
                "target": target,
                "vulnerabilities": [],
                "total_vulnerabilities": 0,
                "severity_distribution": {}
            }
        
        vulnerabilities: List[Dict[str, Any]] = []
        buffer = ""
        line_count = 0
        error_count = 0
        start_time = asyncio.get_event_loop().time()
        
        try:
            while True:
                # Check global timeout
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed > self.timeout:
                    logger.warning(f"Nuclei timeout reached: {elapsed}s")
                    process.kill()
                    await process.wait()
                    break
                
                # Read chunk
                chunk = await process.stdout.read(self.chunk_size)
                if not chunk:
                    break
                
                buffer += chunk.decode("utf-8", errors="replace")
                
                # Prevent buffer overflow
                if len(buffer) > self.max_buffer_size:
                    logger.warning("Buffer size exceeded, discarding oldest data")
                    # Keep only last portion of buffer based on split ratio
                    buffer = buffer[len(buffer) // BUFFER_SPLIT_RATIO:]
                
                # Process complete lines
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    
                    if not line or not line.startswith("{"):
                        continue
                    
                    line_count += 1
                    
                    try:
                        data = json.loads(line)
                        vuln = self._parse_vuln(data)
                        if vuln:
                            vulnerabilities.append(vuln)
                    except json.JSONDecodeError:
                        error_count += 1
                        if error_count <= MAX_ERROR_LOGS:  # Log first few errors only
                            logger.debug(f"Failed to parse JSON line: {line[:100]}")
                    
                    # Safety cap on vulnerabilities
                    if len(vulnerabilities) >= self.max_vulnerabilities:
                        logger.warning(
                            f"Reached max vulnerability limit ({self.max_vulnerabilities}), stopping scan"
                        )
                        process.kill()
                        await process.wait()
                        break
                
                # Break if we hit the vulnerability cap
                if len(vulnerabilities) >= self.max_vulnerabilities:
                    break
            
            # Wait for process to finish
            await process.wait()
        
        except Exception as e:
            logger.exception(f"Nuclei runtime error: {e}")
            if process.returncode is None:
                process.kill()
                await process.wait()
            
            return {
                "status": ScanStatus.FAILED.value,
                "error": str(e),
                "target": target,
                "vulnerabilities": [],
                "total_vulnerabilities": 0,
                "severity_distribution": {}
            }
        
        # Determine final status
        status = ScanStatus.COMPLETED.value
        if line_count > 0 and error_count > line_count * ERROR_RATE_THRESHOLD:
            status = ScanStatus.PARTIAL.value
            logger.warning(f"High error rate in Nuclei scan: {error_count}/{line_count}")
        
        logger.info(
            f"Nuclei scan completed: {target} | vulns={len(vulnerabilities)}, lines={line_count}",
            extra={"target": target}
        )
        
        return {
            "status": status,
            "target": target,
            "vulnerabilities": vulnerabilities,
            "total_vulnerabilities": len(vulnerabilities),
            "severity_distribution": self._severity_dist(vulnerabilities),
            "scan_stats": {
                "lines_processed": line_count,
                "parse_errors": error_count,
                "duration": round(asyncio.get_event_loop().time() - start_time, 2)
            }
        }
    
    def _build_command(self, target: str) -> List[str]:
        """Build Nuclei command with all options"""
        
        command = [
            "nuclei",
            "-u", target,
            "-jsonl",
            "-silent",
            "-no-color",
            "-stats",
            "-rl", str(self.rate_limit),
            "-timeout", "5",
            "-retries", str(settings.NUCLEI_MAX_RETRIES),
            "-no-interactsh",
        ]
        
        if self.severity_filter:
            command.extend(["-severity", ",".join(self.severity_filter)])
        
        if self.template_path:
            command.extend(["-t", self.template_path])
        
        return command
    
    def _parse_vuln(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse vulnerability from Nuclei JSON output.
        Enhanced with more fields.
        """
        
        try:
            info = data.get("info", {})
            classification = info.get("classification", {})
            
            vuln = {
                "template_id": data.get("template-id") or data.get("template"),
                "name": info.get("name"),
                "severity": info.get("severity", "unknown").lower(),
                "matched_at": data.get("matched-at") or data.get("host"),
                "type": data.get("type"),
            }
            
            # Optional fields
            if "description" in info:
                vuln["description"] = info["description"]
            
            # Tags
            if "tags" in info:
                tags = info["tags"]
                if isinstance(tags, str):
                    vuln["tags"] = [t.strip() for t in tags.split(",")]
                elif isinstance(tags, list):
                    vuln["tags"] = tags
            
            # Classification fields
            if classification:
                vuln["cve"] = classification.get("cve-id")
                
                # Handle CVSS score (can be string or number)
                cvss = classification.get("cvss-score")
                if cvss:
                    try:
                        vuln["cvss"] = float(cvss)
                    except (ValueError, TypeError):
                        pass
                
                vuln["cwe"] = classification.get("cwe-id")
                vuln["cvss_metrics"] = classification.get("cvss-metrics")
            
            # References
            if "reference" in info:
                refs = info["reference"]
                if isinstance(refs, str):
                    vuln["references"] = [refs]
                elif isinstance(refs, list):
                    vuln["references"] = refs
            
            # Matcher info
            if "matcher-name" in data:
                vuln["matcher"] = data["matcher-name"]
            
            if "extracted-results" in data:
                vuln["extracted"] = data["extracted-results"]
            
            return vuln
        
        except Exception as e:
            logger.debug(f"Failed to parse vulnerability: {e}")
            return None
    
    def _severity_dist(self, vulns: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate severity distribution"""
        
        dist = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0,
            "unknown": 0
        }
        
        for v in vulns:
            severity = v.get("severity", "unknown").lower()
            if severity in dist:
                dist[severity] += 1
            else:
                dist["unknown"] += 1
        
        return dist


async def run_nuclei_scan(
    target: str,
    timeout: Optional[int] = None,
    severity_filter: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Convenience function to run Nuclei scan.
    
    Args:
        target: Full URL with scheme
        timeout: Optional custom timeout
        severity_filter: Optional severity filter
    
    Returns:
        Scan results dictionary
    """
    scanner = NucleiScanner(timeout=timeout, severity_filter=severity_filter)
    return await scanner.scan(target)