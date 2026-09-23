# app/services/nuclei_scan.py

import asyncio
import json
from typing import Dict, List, Any, Optional

from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.scan import ScanStatus
from app.schemas.stream import StreamLogLevel, StreamStage
from app.services.event_bus import scan_event_bus

logger = get_logger(__name__)

# Constants
BUFFER_SPLIT_RATIO = 2  # Keep 1/2 of buffer when overflow occurs
LOCALHOST_RATE_LIMIT = 200  # Higher rate limit for localhost scans
ERROR_RATE_THRESHOLD = 0.2  # 20% error rate triggers partial status
MAX_ERROR_LOGS = 5  # Maximum number of parse errors to log


class NucleiScanner:
    """
    Async Nuclei scanner with memory safety, buffer management, and live event streaming.
    """
    
    def __init__(
        self,
        timeout: Optional[int] = None,
        rate_limit: Optional[int] = None,
        severity_filter: Optional[List[str]] = None,
        template_path: Optional[str] = None,
        tags: Optional[List[str]] = None,
        templates: Optional[List[str]] = None,
        concurrency: Optional[int] = None,
        scan_id: Optional[str] = None,
    ):
        self.timeout = timeout or settings.NUCLEI_TIMEOUT
        self.rate_limit = rate_limit or settings.NUCLEI_RATE_LIMIT
        self.chunk_size = settings.NUCLEI_BUFFER_SIZE
        self.max_buffer_size = settings.MAX_BUFFER_SIZE
        self.max_vulnerabilities = settings.MAX_VULNERABILITIES
        self.severity_filter = severity_filter
        self.template_path = template_path
        self.tags = tags
        self.templates = templates
        self.concurrency = concurrency
        self.scan_id = scan_id
    
    async def scan(self, target: str) -> Dict[str, Any]:
        """
        Execute Nuclei vulnerability scan.
        
        Args:
            target: Full URL with scheme (http:// or https://)
        
        Returns:
            Scan results dictionary
        """
        
        logger.info(f"Starting Nuclei scan: {target}", extra={"target": target})
        
        if self.scan_id:
            tag_str = ", ".join(self.tags) if self.tags else "cve, misconfig, exposure"
            await scan_event_bus.emit_log(
                self.scan_id,
                f"Starting Nuclei template audit on {target} (tags: [{tag_str}], rate_limit: {self.rate_limit})",
                stage=StreamStage.NUCLEI,
                level=StreamLogLevel.INFO
            )
        
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
        timed_out = False
        start_time = asyncio.get_event_loop().time()
        
        # Concurrently read stderr to prevent OS pipe buffer deadlocks (64KB on Linux)
        stderr_task = asyncio.create_task(process.stderr.read()) if process.stderr else None

        try:
            while True:
                # Check global timeout
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed >= self.timeout:
                    logger.warning(f"Nuclei timeout reached: {elapsed}s")
                    timed_out = True
                    if process.returncode is None:
                        process.kill()
                        await process.wait()
                    break
                
                # Read chunk bounded by remaining timeout
                remaining_time = max(0.01, self.timeout - elapsed)
                try:
                    chunk = await asyncio.wait_for(
                        process.stdout.read(self.chunk_size),
                        timeout=remaining_time
                    )
                except asyncio.TimeoutError:
                    logger.warning(f"Nuclei timeout reached during read: {self.timeout}s")
                    timed_out = True
                    if process.returncode is None:
                        process.kill()
                        await process.wait()
                    break

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
                            if self.scan_id:
                                sev = vuln.get("severity", "info").lower()
                                log_lvl = StreamLogLevel.INFO
                                if sev in ["critical", "high"]:
                                    log_lvl = StreamLogLevel.ERROR
                                elif sev == "medium":
                                    log_lvl = StreamLogLevel.WARNING
                                await scan_event_bus.emit_log(
                                    self.scan_id,
                                    f"[{vuln.get('severity', 'info').upper()}] {vuln.get('name', 'Finding')} ({vuln.get('template_id', '')}) on {vuln.get('matched_at', target)}",
                                    stage=StreamStage.NUCLEI,
                                    level=log_lvl,
                                    details=vuln
                                )
                    except json.JSONDecodeError:
                        error_count += 1
                        if error_count <= MAX_ERROR_LOGS:  # Log first few errors only
                            logger.debug(f"Failed to parse JSON line: {line[:100]}")
                    
                    # Safety cap on vulnerabilities
                    if len(vulnerabilities) >= self.max_vulnerabilities:
                        logger.warning(
                            f"Reached max vulnerability limit ({self.max_vulnerabilities}), stopping scan"
                        )
                        if process.returncode is None:
                            process.kill()
                            await process.wait()
                        break
                
                # Break if we hit the vulnerability cap
                if len(vulnerabilities) >= self.max_vulnerabilities:
                    break
            
            # Wait for process to finish if not already terminated
            if process.returncode is None:
                await process.wait()
            stderr_bytes = await stderr_task if stderr_task else b""
            stderr_output = stderr_bytes.decode("utf-8", errors="replace").strip() if stderr_bytes else ""
        
        except asyncio.CancelledError:
            logger.warning(f"Nuclei scan cancelled for {target}")
            if stderr_task and not stderr_task.done():
                stderr_task.cancel()
            if process and process.returncode is None:
                try:
                    process.kill()
                    await process.wait()
                except Exception:
                    pass
            raise

        except Exception as e:
            logger.exception(f"Nuclei runtime error: {e}")
            if stderr_task and not stderr_task.done():
                stderr_task.cancel()
            if process and process.returncode is None:
                try:
                    process.kill()
                    await process.wait()
                except Exception:
                    pass
            
            return {
                "status": ScanStatus.FAILED.value,
                "error": str(e),
                "target": target,
                "vulnerabilities": [],
                "total_vulnerabilities": 0,
                "severity_distribution": {}
            }
        
        finally:
            if stderr_task and not stderr_task.done():
                stderr_task.cancel()
            if process and process.returncode is None:
                try:
                    process.kill()
                    await process.wait()
                except Exception:
                    pass
        
        # Determine final status
        if timed_out:
            logger.warning(f"Nuclei scan timed out for {target}")
            return {
                "status": ScanStatus.TIMEOUT.value,
                "error": f"Nuclei scan timed out after {self.timeout}s",
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

        # Check if process crashed or failed
        if process.returncode is not None and process.returncode != 0:
            error_msg = stderr_output or f"Nuclei exited with code {process.returncode}"
            logger.error(f"Nuclei failed for {target}: {error_msg}")
            if not vulnerabilities:
                return {
                    "status": ScanStatus.FAILED.value,
                    "error": error_msg,
                    "target": target,
                    "vulnerabilities": [],
                    "total_vulnerabilities": 0,
                    "severity_distribution": {}
                }
            else:
                return {
                    "status": ScanStatus.PARTIAL.value,
                    "error": error_msg,
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

        status = ScanStatus.COMPLETED.value
        if line_count > 0 and error_count > line_count * ERROR_RATE_THRESHOLD:
            status = ScanStatus.PARTIAL.value
            logger.warning(f"High error rate in Nuclei scan: {error_count}/{line_count}")
        
        if self.scan_id:
            await scan_event_bus.emit_log(
                self.scan_id,
                f"Nuclei vulnerability scan finished on {target}: {len(vulnerabilities)} findings detected ({line_count} responses evaluated)",
                stage=StreamStage.NUCLEI,
                level=StreamLogLevel.SUCCESS if not vulnerabilities else StreamLogLevel.WARNING,
                details={"total_vulnerabilities": len(vulnerabilities)}
            )

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
        
        if self.tags:
            cleaned_tags = [t.strip() for t in self.tags if t and t.strip()]
            if cleaned_tags:
                command.extend(["-tags", ",".join(cleaned_tags)])

        if self.templates:
            for tmpl in self.templates:
                if tmpl and tmpl.strip():
                    command.extend(["-t", tmpl.strip()])
        elif self.template_path:
            command.extend(["-t", self.template_path])
        
        if self.concurrency:
            command.extend(["-c", str(self.concurrency)])
        
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
    severity_filter: Optional[List[str]] = None,
    tags: Optional[List[str]] = None,
    templates: Optional[List[str]] = None,
    rate_limit: Optional[int] = None,
    concurrency: Optional[int] = None,
    scan_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convenience function to run Nuclei scan.
    
    Args:
        target: Full URL with scheme
        timeout: Optional custom timeout
        severity_filter: Optional severity filter
        tags: Optional list of Nuclei tags (e.g. ['cve', 'rce'])
        templates: Optional list of specific template paths/IDs
        rate_limit: Optional request rate limit
        concurrency: Optional concurrent template executions
        scan_id: Optional scan ID for streaming logs
    
    Returns:
        Scan results dictionary
    """
    scanner = NucleiScanner(
        timeout=timeout,
        severity_filter=severity_filter,
        tags=tags,
        templates=templates,
        rate_limit=rate_limit,
        concurrency=concurrency,
        scan_id=scan_id,
    )
    return await scanner.scan(target)