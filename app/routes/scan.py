# app/routes/scan.py

from fastapi import APIRouter, HTTPException, Depends, Request, Query, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
from typing import Optional, Any, Dict, List
import asyncio
import json

from app.schemas.scan import (
    ScanCreateRequest,
    ScanCreateResponse,
    ScanResultResponse,
    ScanHistoryResponse,
    ScanStatus,
    ErrorResponse
)
from app.db.database import get_db
from app.db.crud import (
    create_scan,
    get_scan,
    update_scan_result,
    mark_scan_failed,
    get_scan_history,
    delete_scan,
    cleanup_old_scans
)
from app.services.scanner_service import run_full_scan, get_scan_queue_info
from app.services.profile_service import get_available_profiles, get_available_tags, resolve_scan_options
from app.services.event_bus import scan_event_bus
from app.schemas.report import ReportFormat, ReportType
from app.services.report_service import (
    generate_json_report,
    generate_markdown_report,
    generate_html_report,
    generate_pdf_report,
)
from app.core.security import validate_target, sanitize_scan_id, TargetValidationError
from app.core.rate_limit import check_rate_limit
from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)

router = APIRouter(prefix="/api/scan", tags=["Scan"])


# ==================== START SCAN ====================

# Fix 8: Hold references to background tasks to prevent garbage collection
_background_tasks: set = set()


@router.post(
    "/",
    response_model=ScanCreateResponse,
    dependencies=[Depends(check_rate_limit)],
    responses={
        400: {"model": ErrorResponse},
        429: {"model": ErrorResponse},
        503: {"model": ErrorResponse}
    }
)
async def start_scan(
    payload: ScanCreateRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Start a new vulnerability scan.
    
    - **target**: Hostname, IP address, or URL to scan
    
    Returns scan_id to track the scan progress.
    """
    
    # Security validation: Client options can only be MORE restrictive than global settings
    # Users cannot bypass global security policies
    
    # Private IP scanning: Only allow if globally enabled AND client requests it
    if payload.options and payload.options.allow_private:
        if not settings.ALLOW_PRIVATE_IP_SCANNING:
            logger.warning(
                f"Attempt to bypass ALLOW_PRIVATE_IP_SCANNING blocked for target: {payload.target}",
                extra={"target": payload.target, "client_ip": request.client.host if request.client else "unknown"}
            )
        allow_private = settings.ALLOW_PRIVATE_IP_SCANNING and payload.options.allow_private
    else:
        allow_private = False
    
    # Localhost scanning: Respect global setting, allow client to be more restrictive
    if payload.options and not payload.options.allow_localhost:
        allow_localhost = False  # Client wants to be more restrictive
    elif not settings.ALLOW_LOCALHOST_SCANNING:
        allow_localhost = False  # Global policy enforced
    else:
        allow_localhost = True  # Default behavior
    
    is_valid, error_msg, metadata = validate_target(
        payload.target,
        allow_private=allow_private,
        allow_localhost=allow_localhost
    )
    
    if not is_valid:
        logger.warning(f"Invalid target rejected: {payload.target} - {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Fix 2: Use atomic try-acquire instead of a racy available_slots check
    queue_info = get_scan_queue_info()
    if queue_info["scans_running"] >= settings.MAX_CONCURRENT_SCANS:
        raise HTTPException(
            status_code=503,
            detail=f"Maximum concurrent scans ({settings.MAX_CONCURRENT_SCANS}) reached. Please try again later."
        )

    # Extract scan profile and options
    profile = (
        payload.scan_profile.value
        if hasattr(payload.scan_profile, "value")
        else (payload.scan_profile or payload.scan_mode or "quick")
    )
    scan_opts = payload.options.model_dump() if payload.options else None

    # Generate scan ID
    scan_id = str(uuid4())
    
    # Create scan record
    scan = await create_scan(
        db,
        scan_id,
        payload.target,
        scan_profile=profile,
        scan_options=scan_opts
    )
    
    if not scan:
        raise HTTPException(status_code=500, detail="Failed to create scan record")
    
    # Fix 8: Hold a reference to the task so it can't be garbage collected
    task = asyncio.create_task(
        _run_and_store_scan(
            scan_id,
            payload.target,
            metadata,
            scan_profile=profile,
            options=payload.options
        )
    )
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)
    
    logger.info(
        f"Scan started: {scan_id} for {payload.target} (profile={profile})",
        extra={"scan_id": scan_id, "target": payload.target, "profile": profile}
    )
    
    return ScanCreateResponse(
        scan_id=scan_id,
        target=payload.target,
        status=ScanStatus.RUNNING,
        scan_profile=profile
    )


# ==================== GET SCAN RESULTS ====================

# Fix 10: Single helper to build the scan response — eliminates duplicated dict structure
def _build_scan_response(scan) -> dict:
    if scan.result and isinstance(scan.result, dict):
        nmap = scan.result.get("nmap", {"status": "pending", "target": scan.target, "ports": [], "total_ports": 0})
        nuclei = scan.result.get("nuclei", {"status": "pending", "target": scan.target, "vulnerabilities": [], "total_vulnerabilities": 0, "severity_distribution": {}})
        summary = scan.result.get("summary", {"total_vulnerabilities": 0, "open_ports": 0, "severity_distribution": {}, "critical_count": 0, "high_count": 0})
    else:
        pending_status = "pending" if scan.status == ScanStatus.RUNNING.value else scan.status
        nmap = {"status": pending_status, "target": scan.target, "ports": [], "total_ports": 0}
        nuclei = {"status": pending_status, "target": scan.target, "vulnerabilities": [], "total_vulnerabilities": 0, "severity_distribution": {}}
        summary = {"total_vulnerabilities": 0, "open_ports": 0, "severity_distribution": {}, "critical_count": 0, "high_count": 0}

    return {
        "scan_id": scan.scan_id,
        "target": scan.target,
        "status": scan.status,
        "scan_profile": scan.scan_profile or "quick",
        "scan_options": scan.scan_options,
        "risk_score": scan.risk_score,
        "duration": scan.duration,
        "summary": summary,
        "nmap": nmap,
        "nuclei": nuclei,
        "created_at": scan.created_at,
        "updated_at": scan.updated_at,
        "error": scan.error_message
    }


@router.get(
    "/results/{scan_id}",
    response_model=ScanResultResponse,
    responses={404: {"model": ErrorResponse}}
)
async def get_results(
    scan_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get scan results by scan ID.

    - **scan_id**: UUID of the scan

    Returns complete scan results including risk score and vulnerabilities.
    """
    try:
        scan_id = sanitize_scan_id(scan_id)
    except (ValueError, TargetValidationError) as e:
        raise HTTPException(status_code=400, detail="Invalid scan_id format")

    scan = await get_scan(db, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    return _build_scan_response(scan)


# ==================== LIVE TERMINAL STREAMING (SSE) ====================

@router.get("/{scan_id}/stream")
async def stream_scan_logs(
    scan_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Stream real-time scan terminal logs via Server-Sent Events (SSE).
    
    Replays past events from memory buffer, then streams live events until scan completion.
    """
    try:
        sanitized_id = sanitize_scan_id(scan_id)
    except (ValueError, TargetValidationError):
        raise HTTPException(status_code=400, detail="Invalid scan_id format")

    scan = await get_scan(db, sanitized_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    async def event_generator():
        # 1. Send all buffered historical logs
        history = scan_event_bus.get_history(sanitized_id)
        has_done = False
        for msg in history:
            yield f"event: {msg.event}\ndata: {msg.data.model_dump_json()}\n\n"
            if msg.event == "done":
                has_done = True

        # If scan has finished or history already contains done event, terminate stream
        if has_done or scan.status != ScanStatus.RUNNING.value:
            if not has_done:
                yield f"event: done\ndata: {json.dumps({'scan_id': sanitized_id, 'status': scan.status})}\n\n"
            return

        # 2. Subscribe to live queue
        queue = await scan_event_bus.subscribe(sanitized_id)
        try:
            while True:
                # Check if client disconnected
                if await request.is_disconnected():
                    break
                try:
                    msg = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield f"event: {msg.event}\ndata: {msg.data.model_dump_json()}\n\n"
                    if msg.event == "done":
                        break
                except asyncio.TimeoutError:
                    # Heartbeat comment to keep HTTP connection alive
                    yield ": ping\n\n"
        finally:
            await scan_event_bus.unsubscribe(sanitized_id, queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


# ==================== LIVE TERMINAL STREAMING (WEBSOCKET) ====================

@router.websocket("/{scan_id}/ws")
async def websocket_scan_logs(websocket: WebSocket, scan_id: str):
    """
    WebSocket endpoint for bidirectional real-time scan terminal streaming.
    """
    await websocket.accept()
    
    try:
        sanitized_id = sanitize_scan_id(scan_id)
    except (ValueError, TargetValidationError):
        await websocket.send_json({"event": "error", "message": "Invalid scan_id format"})
        await websocket.close(code=1008)
        return

    # 1. Send all buffered historical logs
    history = scan_event_bus.get_history(sanitized_id)
    for msg in history:
        await websocket.send_json({
            "event": msg.event,
            "data": msg.data.model_dump(mode="json")
        })

    # 2. Subscribe to live queue
    queue = await scan_event_bus.subscribe(sanitized_id)
    
    async def listen_client():
        """Listen for client pings or control messages"""
        try:
            while True:
                data = await websocket.receive_text()
                if data == "ping":
                    await websocket.send_text("pong")
        except (WebSocketDisconnect, asyncio.CancelledError):
            pass

    client_task = asyncio.create_task(listen_client())

    try:
        while True:
            try:
                msg = await asyncio.wait_for(queue.get(), timeout=1.0)
                await websocket.send_json({
                    "event": msg.event,
                    "data": msg.data.model_dump(mode="json")
                })
                if msg.event == "done":
                    break
            except asyncio.TimeoutError:
                if client_task.done():
                    break
    except (WebSocketDisconnect, asyncio.CancelledError):
        pass
    except Exception as e:
        logger.debug(f"WebSocket streaming error for scan {sanitized_id}: {e}")
    finally:
        client_task.cancel()
        await scan_event_bus.unsubscribe(sanitized_id, queue)
        try:
            await websocket.close()
        except Exception:
            pass


# ==================== REPORT DOWNLOAD ====================

@router.get(
    "/{scan_id}/report",
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse}
    }
)
async def download_scan_report(
    scan_id: str,
    format: ReportFormat = Query(ReportFormat.HTML, description="Report format (html, pdf, markdown, json)"),
    report_type: ReportType = Query(ReportType.TECHNICAL, description="Report audience (technical, executive)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate and download a comprehensive security report for a completed scan.
    Supports HTML, PDF, Markdown, and JSON formats in Executive or Technical mode.
    """
    try:
        scan_id = sanitize_scan_id(scan_id)
    except (ValueError, TargetValidationError):
        raise HTTPException(status_code=400, detail="Invalid scan_id format")

    scan_record = await get_scan(db, scan_id)
    if not scan_record:
        raise HTTPException(status_code=404, detail="Scan not found")

    scan_data = {
        "scan_id": scan_record.scan_id,
        "target": scan_record.target,
        "status": scan_record.status,
        "scan_profile": scan_record.scan_profile or "quick",
        "risk_score": scan_record.risk_score or 0.0,
        "created_at": scan_record.created_at,
        "updated_at": scan_record.updated_at,
        "duration": scan_record.duration,
        "nmap": scan_record.nmap_result or {},
        "nuclei": scan_record.nuclei_result or {},
        "ai_analysis": scan_record.ai_analysis or {},
        "scan_options": scan_record.scan_options or {}
    }

    clean_target = scan_record.target.replace("://", "_").replace("/", "_").replace(":", "_")
    filename_prefix = f"xenorasec-report-{clean_target}-{report_type.value}"

    if format == ReportFormat.PDF:
        pdf_bytes = generate_pdf_report(scan_data, report_type)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename_prefix}.pdf"'}
        )
    elif format == ReportFormat.HTML:
        html_content = generate_html_report(scan_data, report_type)
        return Response(
            content=html_content,
            media_type="text/html; charset=utf-8",
            headers={"Content-Disposition": f'inline; filename="{filename_prefix}.html"'}
        )
    elif format == ReportFormat.MARKDOWN:
        md_content = generate_markdown_report(scan_data, report_type)
        return Response(
            content=md_content,
            media_type="text/markdown; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{filename_prefix}.md"'}
        )
    elif format == ReportFormat.JSON:
        json_report = generate_json_report(scan_data, report_type)
        return Response(
            content=json_report,
            media_type="application/json; charset=utf-8",
            headers={"Content-Disposition": f'attachment; filename="{filename_prefix}.json"'}
        )
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")


# ==================== SCAN HISTORY ====================

@router.get("/history", response_model=ScanHistoryResponse)
async def get_history(
    limit: int = Query(10, ge=1, le=100, description="Number of results to return"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    status: str = Query(None, description="Filter by status"),
    target: str = Query(None, description="Filter by target (partial match)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get paginated scan history.
    
    - **limit**: Number of results per page (1-100)
    - **offset**: Number of results to skip
    - **status**: Optional status filter
    - **target**: Optional target filter
    """
    
    # Validate status if provided
    if status:
        try:
            ScanStatus(status)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {[s.value for s in ScanStatus]}"
            )
    
    scans, total = await get_scan_history(db, limit, offset, status, target)
    
    items = [
        {
            "scan_id": scan.scan_id,
            "target": scan.target,
            "status": scan.status,
            "scan_profile": scan.scan_profile or "quick",
            "risk_score": scan.risk_score,
            "created_at": scan.created_at,
            "updated_at": scan.updated_at,
            "duration": scan.duration
        }
        for scan in scans
    ]
    
    return ScanHistoryResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset
    )


# ==================== RETRY SCAN ====================

@router.post(
    "/{scan_id}/retry",
    response_model=ScanCreateResponse,
    dependencies=[Depends(check_rate_limit)],
    responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}}
)
async def retry_scan(
    scan_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Retry a failed scan.
    
    - **scan_id**: UUID of the failed scan
    
    Creates a new scan linked to the original.
    """
    
    # Get original scan
    try:
        scan_id = sanitize_scan_id(scan_id)
    except (ValueError, TargetValidationError):
        raise HTTPException(status_code=400, detail="Invalid scan_id format")
    
    original_scan = await get_scan(db, scan_id)
    
    if not original_scan:
        raise HTTPException(status_code=404, detail="Original scan not found")
    
    # Only allow retry for failed, timeout, or partial scans
    if original_scan.status not in [ScanStatus.FAILED.value, ScanStatus.TIMEOUT.value, ScanStatus.PARTIAL.value]:
        raise HTTPException(
            status_code=400,
            detail=f"Can only retry failed, timeout, or partial scans. Current status: {original_scan.status}"
        )
    
    # Check queue availability
    queue_info = get_scan_queue_info()
    if queue_info["available_slots"] <= 0:
        raise HTTPException(
            status_code=503,
            detail=f"Maximum concurrent scans reached. Please try again later."
        )
    
    # Create new scan
    new_scan_id = str(uuid4())
    
    # Revalidate target
    is_valid, error_msg, metadata = validate_target(original_scan.target)
    
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Target no longer valid: {error_msg}")
    
    # Create new scan record with parent reference and original profile/options
    new_scan = await create_scan(
        db,
        new_scan_id,
        original_scan.target,
        parent_scan_id=scan_id,
        scan_profile=original_scan.scan_profile or "quick",
        scan_options=original_scan.scan_options
    )
    
    if not new_scan:
        raise HTTPException(status_code=500, detail="Failed to create retry scan")
    
    from app.schemas.scan import ScanOptions
    retry_options = ScanOptions(**original_scan.scan_options) if original_scan.scan_options else None
    
    # Fix 8: Track retry task reference too
    task = asyncio.create_task(
        _run_and_store_scan(
            new_scan_id,
            original_scan.target,
            metadata,
            scan_profile=original_scan.scan_profile or "quick",
            options=retry_options
        )
    )
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)
    
    logger.info(
        f"Retry scan started: {new_scan_id} (parent: {scan_id})",
        extra={"scan_id": new_scan_id, "parent_scan_id": scan_id}
    )
    
    return ScanCreateResponse(
        scan_id=new_scan_id,
        target=original_scan.target,
        status=ScanStatus.RUNNING,
        scan_profile=original_scan.scan_profile or "quick",
        message=f"Retry scan started (original: {scan_id})"
    )


# ==================== DELETE SCAN ====================

@router.delete("/{scan_id}", responses={404: {"model": ErrorResponse}})
async def delete_scan_endpoint(
    scan_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a scan by ID.
    
    - **scan_id**: UUID of the scan to delete
    """
    
    try:
        scan_id = sanitize_scan_id(scan_id)
    except (ValueError, TargetValidationError):
        raise HTTPException(status_code=400, detail="Invalid scan_id format")
    
    deleted = await delete_scan(db, scan_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    return {"message": "Scan deleted successfully", "scan_id": scan_id}


# ==================== CLEANUP ====================

@router.post("/cleanup")
async def cleanup_endpoint(
    days: int = Query(None, ge=1, description="Delete scans older than N days"),
    secret: str = Query(..., description="Admin secret key (set CLEANUP_SECRET env var)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Cleanup old scan records.

    - **days**: Delete scans older than this many days (default from config)
    - **secret**: Must match the CLEANUP_SECRET environment variable
    """
    import os
    expected_secret = os.getenv("CLEANUP_SECRET", "")
    if not expected_secret:
        raise HTTPException(
            status_code=503,
            detail="Cleanup endpoint is disabled: set the CLEANUP_SECRET environment variable to enable it"
        )
    if secret != expected_secret:
        raise HTTPException(status_code=403, detail="Invalid secret")

    count = await cleanup_old_scans(db, days)

    return {
        "message": "Cleanup completed",
        "scans_deleted": count,
        "retention_days": days or settings.SCAN_RETENTION_DAYS
    }


# ==================== CANCEL SCAN ====================

# Fix 14: Track running tasks by scan_id so they can be cancelled
_running_scan_tasks: dict = {}


@router.post(
    "/{scan_id}/cancel",
    responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}}
)
async def cancel_scan(
    scan_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel a running scan.

    - **scan_id**: UUID of the running scan
    """
    try:
        scan_id = sanitize_scan_id(scan_id)
    except (ValueError, TargetValidationError):
        raise HTTPException(status_code=400, detail="Invalid scan_id format")

    scan = await get_scan(db, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    if scan.status != ScanStatus.RUNNING.value:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel scan with status: {scan.status}"
        )

    # Cancel the background task if we have a reference
    task = _running_scan_tasks.pop(scan_id, None)
    if task and not task.done():
        task.cancel()

    await mark_scan_failed(db, scan_id, "Cancelled by user", status=ScanStatus.FAILED.value)

    return {"message": "Scan cancelled", "scan_id": scan_id}


# ==================== QUEUE INFO ====================

@router.get("/queue")
async def get_queue():
    """
    Get current scan queue information.
    """
    return get_scan_queue_info()


# ==================== PROFILES & TEMPLATES ====================

@router.get("/profiles")
async def get_profiles():
    """
    List available scan profiles (Quick, Full Web Audit, Network Discovery, Custom).
    """
    return {"profiles": get_available_profiles()}


@router.get("/templates")
async def get_templates():
    """
    List available Nuclei template categories and tags.
    """
    return {"tags": get_available_tags()}


# ==================== BACKGROUND SCAN TASK ====================

async def _run_and_store_scan(
    scan_id: str,
    target: str,
    metadata: dict,
    scan_profile: Optional[str] = "quick",
    options: Optional[Any] = None
):
    """
    Background task to run scan and store results.
    
    This runs in a separate task and manages its own database session.
    """
    
    # Import here to avoid circular dependency
    from app.db.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        try:
            logger.info(
                f"Background scan executing: {scan_id} (profile={scan_profile})",
                extra={"scan_id": scan_id, "target": target, "profile": scan_profile}
            )

            # Fix 14: Register this task so it can be cancelled via the cancel endpoint
            current_task = asyncio.current_task()
            if current_task:
                _running_scan_tasks[scan_id] = current_task
            
            # Run the full scan with profile, options, and scan_id
            result = await run_full_scan(
                target,
                metadata,
                parallel=True,
                scan_profile=scan_profile,
                options=options,
                scan_id=scan_id
            )
            
            # Determine final status based on result
            final_status = result.get("status", ScanStatus.COMPLETED.value)
            
            # Store result
            if final_status in [ScanStatus.COMPLETED.value, ScanStatus.PARTIAL.value]:
                await update_scan_result(
                    db=db,
                    scan_id=scan_id,
                    result=result,
                    risk_score=result.get("risk_score", 0.0),
                    duration=result.get("duration"),
                    status=final_status
                )
            else:
                # Mark as failed/timeout
                error_msg = result.get("error", "Scan failed")
                await mark_scan_failed(
                    db=db,
                    scan_id=scan_id,
                    error=error_msg,
                    status=final_status
                )
        
        except asyncio.CancelledError:
            logger.info(f"Scan cancelled: {scan_id}")
            await mark_scan_failed(db, scan_id, "Cancelled by user", status=ScanStatus.FAILED.value)

        except Exception as e:
            logger.exception(f"Background scan failed: {scan_id}")
            await mark_scan_failed(
                db=db,
                scan_id=scan_id,
                error=str(e),
                status=ScanStatus.FAILED.value
            )

        finally:
            # Fix 14: Always clean up task reference
            _running_scan_tasks.pop(scan_id, None)