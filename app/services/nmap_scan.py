# app/services/nmap_scan.py

import asyncio
import xml.etree.ElementTree as ET
from typing import Dict, List, Any, Optional

from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.scan import ScanStatus

logger = get_logger(__name__)

# Constants
RETRY_DELAY_SECONDS = 2  # Delay between retry attempts
LOCALHOST_TIMING = "T5"  # Aggressive timing for localhost scans
DEFAULT_TIMING_FALLBACK = "T4"  # Default timing if not set


class NmapScanner:
    """
    Async Nmap scanner with configurable settings.
    """
    
    def __init__(
        self,
        timeout: Optional[int] = None,
        timing: Optional[str] = None,
        max_retries: Optional[int] = None
    ):
        self.timeout = timeout or settings.NMAP_TIMEOUT
        self.timing = timing or settings.NMAP_TIMING
        self.max_retries = max_retries or settings.NMAP_MAX_RETRIES
    
    async def scan(self, target: str) -> Dict[str, Any]:
        """
        Execute Nmap scan against target.
        
        Args:
            target: Hostname or IP address (NOT URL)
        
        Returns:
            Scan results dictionary
        """
        
        logger.info(f"Starting Nmap scan: {target}", extra={"target": target})
        
        # Optimize for localhost
        if target.startswith("127.") or target == "localhost":
            self.timing = LOCALHOST_TIMING
            logger.debug("Using aggressive timing for localhost")
        
        for attempt in range(self.max_retries):
            try:
                result = await self._execute_scan(target)
                
                if result.get("status") == ScanStatus.COMPLETED.value:
                    logger.info(
                        f"Nmap scan completed: {target} | ports={result.get('total_ports', 0)}",
                        extra={"target": target}
                    )
                    return result
                
                # Fix 3: Never retry a timeout — it will just time out again
                if result.get("status") == ScanStatus.TIMEOUT.value:
                    logger.warning(f"Nmap timed out for {target}, not retrying")
                    return result
                
                if attempt < self.max_retries - 1:
                    logger.warning(f"Nmap retry {attempt + 1}/{self.max_retries} for {target}")
                    await asyncio.sleep(RETRY_DELAY_SECONDS)
            
            except Exception as e:
                logger.error(f"Nmap scan exception (attempt {attempt + 1}): {e}")
                if attempt == self.max_retries - 1:
                    return {
                        "status": ScanStatus.FAILED.value,
                        "error": str(e),
                        "target": target,
                        "ports": [],
                        "total_ports": 0
                    }
        
        # If we reach here, all retries failed without returning
        return {
            "status": ScanStatus.FAILED.value,
            "error": "All retry attempts failed without completing scan",
            "target": target,
            "ports": [],
            "total_ports": 0
        }
    
    async def _execute_scan(self, target: str) -> Dict[str, Any]:
        """Execute single Nmap scan attempt"""
        
        command = [
            "nmap",
            "-sT",  # TCP connect scan (doesn't require root)
            "-sV",  # Service version detection
            f"-{self.timing}",  # Timing template
            "-Pn",  # Skip host discovery
            "--open",  # Only show open ports
            "-oX", "-",  # XML output to stdout
            "--max-retries", str(self.max_retries),
            "--host-timeout", f"{self.timeout}s",
            target
        ]
        
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout + 10
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                logger.warning(f"Nmap timeout for {target}")
                return {
                    "status": ScanStatus.TIMEOUT.value,
                    "target": target,
                    "ports": [],
                    "total_ports": 0
                }
            
            if process.returncode != 0:
                error_msg = stderr.decode().strip()
                logger.error(f"Nmap failed: {error_msg}")
                return {
                    "status": ScanStatus.FAILED.value,
                    "error": error_msg or "Nmap scan failed",
                    "target": target,
                    "ports": [],
                    "total_ports": 0
                }
            
            xml_output = stdout.decode()
            return self._parse_xml(xml_output, target)
        
        except FileNotFoundError:
            logger.error("Nmap not installed on system")
            return {
                "status": ScanStatus.FAILED.value,
                "error": "Nmap not installed",
                "target": target,
                "ports": [],
                "total_ports": 0
            }
        
        except Exception as e:
            logger.exception(f"Nmap execution error: {e}")
            return {
                "status": ScanStatus.FAILED.value,
                "error": str(e),
                "target": target,
                "ports": [],
                "total_ports": 0
            }
    
    def _parse_xml(self, xml_data: str, target: str) -> Dict[str, Any]:
        """
        Parse Nmap XML output with fallback for partial data recovery.
        
        If XML is corrupted, attempts to parse what's available and returns
        PARTIAL status instead of FAILED.
        """
        
        is_partial_recovery = False
        
        try:
            root = ET.fromstring(xml_data)
        except ET.ParseError as e:
            logger.error(f"XML parse error: {e}")
            
            # Attempt to recover partial XML data
            try:
                # Find the last complete closing tag
                last_close = xml_data.rfind('</')
                if last_close > 0:
                    # Try to close the XML properly
                    truncated = xml_data[:last_close]
                    # Add closing tags for common Nmap structure
                    if '</host>' not in truncated[max(0, last_close-100):]:
                        truncated += '</host>'
                    if '</nmaprun>' not in truncated:
                        truncated += '</nmaprun>'
                    
                    root = ET.fromstring(truncated)
                    is_partial_recovery = True
                    logger.warning(f"Recovered partial XML data for {target}")
                else:
                    raise ET.ParseError("Cannot recover XML")
                    
            except (ET.ParseError, Exception) as recovery_error:
                logger.error(f"XML recovery failed: {recovery_error}")
                return {
                    "status": ScanStatus.FAILED.value,
                    "error": f"Failed to parse Nmap XML output: {str(e)}",
                    "target": target,
                    "ports": [],
                    "total_ports": 0
                }
        
        ports_data: List[Dict[str, Any]] = []
        host_info = {}
        
        for host in root.findall("host"):
            # Host status
            status_elem = host.find("status")
            if status_elem is not None:
                host_info["status"] = status_elem.get("state")
            
            # IP address
            address_elem = host.find("address")
            if address_elem is not None:
                host_info["ip"] = address_elem.get("addr")
                host_info["addr_type"] = address_elem.get("addrtype")
            
            # Hostname
            hostnames = host.find("hostnames")
            if hostnames is not None:
                hostname_list = []
                for hostname in hostnames.findall("hostname"):
                    if hostname.get("name"):
                        hostname_list.append(hostname.get("name"))
                if hostname_list:
                    host_info["hostnames"] = hostname_list
            
            # Parse ports
            ports_elem = host.find("ports")
            if ports_elem is not None:
                for port in ports_elem.findall("port"):
                    state_elem = port.find("state")
                    if state_elem is None or state_elem.get("state") != "open":
                        continue
                    
                    service_elem = port.find("service")
                    
                    port_data = {
                        "port": int(port.get("portid")),
                        "protocol": port.get("protocol"),
                        "service": service_elem.get("name") if service_elem is not None else None,
                        "product": service_elem.get("product") if service_elem is not None else None,
                        "version": service_elem.get("version") if service_elem is not None else None,
                        "extrainfo": service_elem.get("extrainfo") if service_elem is not None else None,
                    }
                    
                    ports_data.append(port_data)
        
        # Determine status based on whether recovery was needed
        status = ScanStatus.PARTIAL.value if is_partial_recovery else ScanStatus.COMPLETED.value
        
        return {
            "status": status,
            "target": target,
            "host_info": host_info,
            "ports": ports_data,
            "total_ports": len(ports_data),
        }


async def run_nmap_scan(target: str) -> Dict[str, Any]:
    """
    Convenience function to run Nmap scan.
    
    Args:
        target: Target hostname or IP (NOT URL)
    
    Returns:
        Scan results dictionary
    """
    scanner = NmapScanner()
    return await scanner.scan(target)