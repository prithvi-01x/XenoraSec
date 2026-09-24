# app/services/scanner_service.py

import asyncio
import time
from typing import Dict, Any, Optional

from app.services.nmap_scan import run_nmap_scan
from app.services.nuclei_scan import run_nuclei_scan
from app.services.ai_service import analyze_vulnerability_report
from app.services.profile_service import resolve_scan_options
from app.services.event_bus import scan_event_bus
from app.schemas.stream import StreamLogLevel, StreamStage
from app.core.security import prepare_nmap_target, prepare_nuclei_target
from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.scan import ScanStatus, ScanOptions

logger = get_logger(__name__)

# Global semaphore for concurrency control
_scan_semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_SCANS)


async def run_full_scan(
    target: str,
    metadata: dict,
    parallel: bool = True,
    scan_profile: Optional[str] = "quick",
    options: Optional[ScanOptions] = None,
    scan_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Full scan orchestrator with concurrency control and timeout.
    
    Executes:
        1. Nmap port scan with configured port range and timing
        2. Nuclei vulnerability scan with profile tags and templates
        3. AI risk analysis
    
    Args:
        target: Original target string
        metadata: Target metadata from validation
        parallel: Run scans in parallel (True) or sequential (False)
        scan_profile: Scan profile name ('quick', 'full', 'network', 'custom')
        options: Optional ScanOptions overrides
        scan_id: Optional scan ID for streaming telemetry
    
    Returns:
        Complete scan results with risk score, profile, and summary
    """
    
    resolved_options = resolve_scan_options(scan_profile, options)
    
    # Prepare targets for each scanner
    nmap_target = prepare_nmap_target(target, metadata)
    nuclei_target = prepare_nuclei_target(target, metadata)
    
    logger.info(
        f"[SCAN START] {target} (profile={resolved_options['profile']}, parallel={parallel})",
        extra={"target": target, "profile": resolved_options['profile']}
    )
    
    if scan_id:
        await scan_event_bus.emit_log(
            scan_id,
            f"Orchestrator initialized scan for target {target} [Profile: {resolved_options['profile'].upper()}]",
            stage=StreamStage.INIT,
            level=StreamLogLevel.INFO
        )
    
    # Acquire semaphore for concurrency control
    async with _scan_semaphore:
        start_time = time.time()
        try:
            # Global scan timeout wrapper
            scan_result = await asyncio.wait_for(
                _execute_scan(nmap_target, nuclei_target, target, parallel, resolved_options, scan_id),
                timeout=settings.GLOBAL_SCAN_TIMEOUT
            )
            
            duration = round(time.time() - start_time, 2)
            scan_result["duration"] = duration
            
            logger.info(
                f"[SCAN COMPLETE] {target} in {duration}s | "
                f"risk={scan_result.get('risk_score', 0)} | "
                f"ports={scan_result.get('nmap', {}).get('total_ports', 0)} | "
                f"vulns={scan_result.get('nuclei', {}).get('total_vulnerabilities', 0)}",
                extra={"target": target, "duration": duration}
            )
            
            if scan_id:
                final_status = scan_result.get("status", ScanStatus.COMPLETED.value)
                await scan_event_bus.emit_log(
                    scan_id,
                    f"Scan execution finalized in {duration}s. Final status: {final_status.upper()}",
                    stage=StreamStage.COMPLETE,
                    level=StreamLogLevel.SUCCESS if final_status == ScanStatus.COMPLETED.value else StreamLogLevel.WARNING,
                    event_name="done"
                )
            
            return scan_result
        
        except asyncio.TimeoutError:
            duration = round(time.time() - start_time, 2)
            logger.error(f"[SCAN TIMEOUT] {target} after {duration}s")
            
            return {
                "target": target,
                "duration": duration,
                "risk_score": 0.0,
                "status": ScanStatus.TIMEOUT.value,
                "summary": {
                    "total_vulnerabilities": 0,
                    "open_ports": 0,
                    "severity_distribution": {},
                    "critical_count": 0,
                    "high_count": 0
                },
                "error": f"Scan exceeded global timeout of {settings.GLOBAL_SCAN_TIMEOUT}s",
                "nmap": {"status": ScanStatus.TIMEOUT.value, "error": "Global timeout", "ports": [], "total_ports": 0},
                "nuclei": {"status": ScanStatus.TIMEOUT.value, "error": "Global timeout", "vulnerabilities": [], "total_vulnerabilities": 0},
            }
        
        except Exception as e:
            duration = round(time.time() - start_time, 2)
            logger.exception(f"[SCAN FATAL ERROR] {target}")
            
            return {
                "target": target,
                "duration": duration,
                "risk_score": 0.0,
                "status": ScanStatus.FAILED.value,
                "summary": {
                    "total_vulnerabilities": 0,
                    "open_ports": 0,
                    "severity_distribution": {},
                    "critical_count": 0,
                    "high_count": 0
                },
                "error": str(e),
                "nmap": {"status": ScanStatus.FAILED.value, "error": "Fatal scan error", "ports": [], "total_ports": 0},
                "nuclei": {"status": ScanStatus.FAILED.value, "error": "Fatal scan error", "vulnerabilities": [], "total_vulnerabilities": 0},
            }


async def _execute_scan(
    nmap_target: str,
    nuclei_target: str,
    original_target: str,
    parallel: bool,
    resolved_options: Optional[Dict[str, Any]] = None,
    scan_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Internal scan execution logic.
    """
    options = resolved_options or {}
    port_range = options.get("port_range")
    nmap_timing = options.get("nmap_timing")
    nuclei_tags = options.get("nuclei_tags")
    nuclei_templates = options.get("nuclei_templates")
    severity_filter = options.get("severity_filter")
    rate_limit = options.get("rate_limit")
    concurrency = options.get("concurrency")
    
    # ==================== PARALLEL MODE ====================
    if parallel:
        nmap_result, nuclei_result = await asyncio.gather(
            run_nmap_scan(nmap_target, timing=nmap_timing, port_range=port_range, scan_id=scan_id),
            run_nuclei_scan(
                nuclei_target,
                tags=nuclei_tags,
                templates=nuclei_templates,
                severity_filter=severity_filter,
                rate_limit=rate_limit,
                concurrency=concurrency,
                scan_id=scan_id
            ),
            return_exceptions=True
        )
    
    # ==================== SEQUENTIAL MODE ====================
    else:
        nmap_result = await run_nmap_scan(nmap_target, timing=nmap_timing, port_range=port_range, scan_id=scan_id)
        nuclei_result = await run_nuclei_scan(
            nuclei_target,
            tags=nuclei_tags,
            templates=nuclei_templates,
            severity_filter=severity_filter,
            rate_limit=rate_limit,
            concurrency=concurrency,
            scan_id=scan_id
        )
    
    # ==================== HANDLE EXCEPTIONS ====================
    if isinstance(nmap_result, Exception):
        logger.error(f"Nmap exception: {nmap_result}")
        nmap_result = {
            "status": ScanStatus.FAILED.value,
            "error": str(nmap_result),
            "target": nmap_target,
            "ports": [],
            "total_ports": 0
        }
    
    if isinstance(nuclei_result, Exception):
        logger.error(f"Nuclei exception: {nuclei_result}")
        nuclei_result = {
            "status": ScanStatus.FAILED.value,
            "error": str(nuclei_result),
            "target": nuclei_target,
            "vulnerabilities": [],
            "total_vulnerabilities": 0,
            "severity_distribution": {}
        }
    
    # ==================== AI ANALYSIS ====================
    # Fix 13: Warn if Nuclei is running despite 0 open ports (likely wasteful)
    nmap_ports = nmap_result.get("total_ports", 0) if not isinstance(nmap_result, Exception) else 0
    if nmap_ports == 0 and nmap_result.get("status") == ScanStatus.COMPLETED.value:
        logger.warning(
            f"Nmap found 0 open ports on {original_target} — Nuclei scan will likely find nothing. "
            "Consider skipping Nuclei for hosts with no open ports."
        )

    if scan_id:
        await scan_event_bus.emit_log(
            scan_id,
            f"Initiating AI risk modeling and vulnerability correlation for {original_target}...",
            stage=StreamStage.AI,
            level=StreamLogLevel.INFO
        )

    try:
        analysis = await analyze_vulnerability_report(
            nmap_result=nmap_result,
            nuclei_result=nuclei_result
        )
        if scan_id:
            await scan_event_bus.emit_log(
                scan_id,
                f"AI Risk Assessment concluded: Risk Score {analysis['risk_score']}/10",
                stage=StreamStage.AI,
                level=StreamLogLevel.SUCCESS,
                details=analysis.get("summary")
            )
    except Exception as e:
        logger.error(f"AI analysis failed: {e}")
        analysis = {
            "risk_score": 0.0,
            "summary": {
                "total_vulnerabilities": 0,
                "open_ports": 0,
                "severity_distribution": {},
                "critical_count": 0,
                "high_count": 0
            }
        }
    
    # ==================== DETERMINE OVERALL STATUS ====================
    nmap_status = nmap_result.get("status", ScanStatus.FAILED.value)
    nuclei_status = nuclei_result.get("status", ScanStatus.FAILED.value)
    
    if nmap_status == ScanStatus.FAILED.value and nuclei_status == ScanStatus.FAILED.value:
        overall_status = ScanStatus.FAILED.value
    elif nmap_status == ScanStatus.TIMEOUT.value or nuclei_status == ScanStatus.TIMEOUT.value:
        overall_status = ScanStatus.TIMEOUT.value
    elif nmap_status == ScanStatus.PARTIAL.value or nuclei_status == ScanStatus.PARTIAL.value:
        overall_status = ScanStatus.PARTIAL.value
    elif nmap_status == ScanStatus.COMPLETED.value and nuclei_status == ScanStatus.COMPLETED.value:
        overall_status = ScanStatus.COMPLETED.value
    else:
        overall_status = ScanStatus.PARTIAL.value
    
    # ==================== BUILD RESULT ====================
    result = {
        "target": original_target,
        "status": overall_status,
        "scan_profile": options.get("profile", "quick"),
        "scan_options": options,
        "risk_score": analysis["risk_score"],
        "summary": analysis["summary"],
        "nmap": nmap_result,
        "nuclei": nuclei_result,
    }
    
    return result


def get_scan_queue_info() -> dict:
    """
    Get information about scan queue.
    
    Returns:
        Dictionary with queue info
    """
    return {
        "max_concurrent_scans": settings.MAX_CONCURRENT_SCANS,
        "available_slots": _scan_semaphore._value,
        "scans_running": settings.MAX_CONCURRENT_SCANS - _scan_semaphore._value,
    }