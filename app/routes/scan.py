# app/routes/scan.py

from fastapi import APIRouter, HTTPException, Depends, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4
import asyncio

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
from app.core.security import validate_target, sanitize_scan_id
from app.core.rate_limit import check_rate_limit
from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)

router = APIRouter(prefix="/api/scan", tags=["Scan"])


# ==================== START SCAN ====================

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
    
    # Check scan queue availability
    queue_info = get_scan_queue_info()
    if queue_info["available_slots"] <= 0:
        raise HTTPException(
            status_code=503,
            detail=f"Maximum concurrent scans ({settings.MAX_CONCURRENT_SCANS}) reached. Please try again later."
        )
    
    # Generate scan ID
    scan_id = str(uuid4())
    
    # Create scan record
    scan = await create_scan(db, scan_id, payload.target)
    
    if not scan:
        raise HTTPException(status_code=500, detail="Failed to create scan record")
    
    # Start scan in background
    asyncio.create_task(
        _run_and_store_scan(scan_id, payload.target, metadata)
    )
    
    logger.info(
        f"Scan started: {scan_id} for {payload.target}",
        extra={"scan_id": scan_id, "target": payload.target}
    )
    
    return ScanCreateResponse(
        scan_id=scan_id,
        target=payload.target,
        status=ScanStatus.RUNNING
    )


# ==================== GET SCAN RESULTS ====================

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
    
    # Sanitize scan_id
    try:
        scan_id = sanitize_scan_id(scan_id)
    except (ValueError, TargetValidationError) as e:
        raise HTTPException(status_code=400, detail="Invalid scan_id format")
    
    # Get scan from database
    scan = await get_scan(db, scan_id)
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    # Build response - handle running scans with no results yet
    if scan.result and isinstance(scan.result, dict):
        # Scan has completed with results
        return {
            "scan_id": scan.scan_id,
            "target": scan.target,
            "status": scan.status,
            "risk_score": scan.risk_score,
            "duration": scan.duration,
            "summary": scan.result.get("summary", {
                "total_vulnerabilities": 0,
                "open_ports": 0,
                "severity_distribution": {},
                "critical_count": 0,
                "high_count": 0
            }),
            "nmap": scan.result.get("nmap", {
                "status": "pending",
                "target": scan.target,
                "ports": [],
                "total_ports": 0
            }),
            "nuclei": scan.result.get("nuclei", {
                "status": "pending",
                "target": scan.target,
                "vulnerabilities": [],
                "total_vulnerabilities": 0,
                "severity_distribution": {}
            }),
            "created_at": scan.created_at,
            "updated_at": scan.updated_at,
            "error": scan.error_message
        }
    else:
        # Scan is still running or failed without results
        return {
            "scan_id": scan.scan_id,
            "target": scan.target,
            "status": scan.status,
            "risk_score": scan.risk_score,
            "duration": scan.duration,
            "summary": {
                "total_vulnerabilities": 0,
                "open_ports": 0,
                "severity_distribution": {},
                "critical_count": 0,
                "high_count": 0
            },
            "nmap": {
                "status": "pending" if scan.status == ScanStatus.RUNNING.value else scan.status,
                "target": scan.target,
                "ports": [],
                "total_ports": 0
            },
            "nuclei": {
                "status": "pending" if scan.status == ScanStatus.RUNNING.value else scan.status,
                "target": scan.target,
                "vulnerabilities": [],
                "total_vulnerabilities": 0,
                "severity_distribution": {}
            },
            "created_at": scan.created_at,
            "updated_at": scan.updated_at,
            "error": scan.error_message
        }


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
    
    # Only allow retry for failed scans
    if original_scan.status not in [ScanStatus.FAILED.value, ScanStatus.TIMEOUT.value]:
        raise HTTPException(
            status_code=400,
            detail=f"Can only retry failed or timeout scans. Current status: {original_scan.status}"
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
    
    # Create new scan record with parent reference
    new_scan = await create_scan(db, new_scan_id, original_scan.target, parent_scan_id=scan_id)
    
    if not new_scan:
        raise HTTPException(status_code=500, detail="Failed to create retry scan")
    
    # Start scan in background
    asyncio.create_task(
        _run_and_store_scan(new_scan_id, original_scan.target, metadata)
    )
    
    logger.info(
        f"Retry scan started: {new_scan_id} (parent: {scan_id})",
        extra={"scan_id": new_scan_id, "parent_scan_id": scan_id}
    )
    
    return ScanCreateResponse(
        scan_id=new_scan_id,
        target=original_scan.target,
        status=ScanStatus.RUNNING,
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
    db: AsyncSession = Depends(get_db)
):
    """
    Cleanup old scan records.
    
    - **days**: Delete scans older than this many days (default from config)
    """
    
    count = await cleanup_old_scans(db, days)
    
    return {
        "message": f"Cleanup completed",
        "scans_deleted": count,
        "retention_days": days or settings.SCAN_RETENTION_DAYS
    }


# ==================== QUEUE INFO ====================

@router.get("/queue")
async def get_queue():
    """
    Get current scan queue information.
    """
    return get_scan_queue_info()


# ==================== BACKGROUND SCAN TASK ====================

async def _run_and_store_scan(scan_id: str, target: str, metadata: dict):
    """
    Background task to run scan and store results.
    
    This runs in a separate task and manages its own database session.
    """
    
    # Import here to avoid circular dependency
    from app.db.database import AsyncSessionLocal
    
    async with AsyncSessionLocal() as db:
        try:
            logger.info(
                f"Background scan executing: {scan_id}",
                extra={"scan_id": scan_id, "target": target}
            )
            
            # Run the full scan
            result = await run_full_scan(target, metadata, parallel=True)
            
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
        
        except Exception as e:
            logger.exception(f"Background scan failed: {scan_id}")
            await mark_scan_failed(
                db=db,
                scan_id=scan_id,
                error=str(e),
                status=ScanStatus.FAILED.value
            )