# app/db/crud.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List, Tuple
from datetime import datetime, timezone, timedelta

from app.db.models import ScanResult
from app.schemas.scan import ScanStatus
from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)


# ==================== CREATE ====================

async def create_scan(
    db: AsyncSession,
    scan_id: str,
    target: str,
    parent_scan_id: Optional[str] = None
) -> Optional[ScanResult]:
    """
    Create a new scan record in the database.
    
    Args:
        db: Database session
        scan_id: Unique scan identifier (UUID)
        target: Target hostname/IP/URL
        parent_scan_id: Optional parent scan ID for retries
    
    Returns:
        ScanResult object or None if creation fails
    """
    try:
        scan = ScanResult(
            scan_id=scan_id,
            target=target,
            status=ScanStatus.RUNNING.value,
            risk_score=0.0,
            result=None,
            parent_scan_id=parent_scan_id,
        )
        
        db.add(scan)
        await db.commit()
        await db.refresh(scan)
        
        logger.info(f"Created scan: {scan_id} for target: {target}")
        return scan
        
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Failed to create scan {scan_id}: {e}")
        return None


# ==================== UPDATE ====================

async def update_scan_result(
    db: AsyncSession,
    scan_id: str,
    result: dict,
    risk_score: float,
    duration: Optional[float] = None,
    status: str = ScanStatus.COMPLETED.value
) -> Optional[ScanResult]:
    """
    Update scan with results after successful completion.
    
    Args:
        db: Database session
        scan_id: Scan identifier
        result: Complete scan result dictionary
        risk_score: Calculated risk score
        duration: Scan duration in seconds
        status: Final status (default: completed)
    
    Returns:
        Updated ScanResult or None if not found
    """
    try:
        query = select(ScanResult).where(ScanResult.scan_id == scan_id)
        res = await db.execute(query)
        scan = res.scalar_one_or_none()
        
        if not scan:
            logger.warning(f"Scan not found for update: {scan_id}")
            return None
        
        scan.result = result
        scan.status = status
        scan.risk_score = risk_score
        scan.duration = duration
        scan.updated_at = datetime.now(timezone.utc)
        
        await db.commit()
        await db.refresh(scan)
        
        logger.info(f"Updated scan {scan_id}: status={status}, risk={risk_score}")
        return scan
        
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Failed to update scan {scan_id}: {e}")
        return None


async def mark_scan_failed(
    db: AsyncSession,
    scan_id: str,
    error: str,
    status: str = ScanStatus.FAILED.value
) -> Optional[ScanResult]:
    """
    Mark scan as failed with error message.
    
    Args:
        db: Database session
        scan_id: Scan identifier
        error: Error message
        status: Status to set (default: failed, can be timeout/partial)
    
    Returns:
        Updated ScanResult or None if not found
    """
    try:
        query = select(ScanResult).where(ScanResult.scan_id == scan_id)
        res = await db.execute(query)
        scan = res.scalar_one_or_none()
        
        if not scan:
            logger.warning(f"Scan not found to mark failed: {scan_id}")
            return None
        
        scan.status = status
        scan.error_message = error
        scan.result = {"error": error}
        scan.updated_at = datetime.now(timezone.utc)
        
        await db.commit()
        await db.refresh(scan)
        
        logger.error(f"Marked scan {scan_id} as {status}: {error}")
        return scan
        
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Failed to mark scan {scan_id} as failed: {e}")
        return None


# ==================== READ ====================

async def get_scan(
    db: AsyncSession,
    scan_id: str
) -> Optional[ScanResult]:
    """
    Retrieve scan by ID.
    
    Args:
        db: Database session
        scan_id: Scan identifier
    
    Returns:
        ScanResult or None if not found
    """
    try:
        query = select(ScanResult).where(ScanResult.scan_id == scan_id)
        res = await db.execute(query)
        return res.scalar_one_or_none()
        
    except SQLAlchemyError as e:
        logger.error(f"Failed to get scan {scan_id}: {e}")
        return None


async def get_scan_history(
    db: AsyncSession,
    limit: int = 10,
    offset: int = 0,
    status: Optional[str] = None,
    target: Optional[str] = None
) -> Tuple[List[ScanResult], int]:
    """
    Get paginated scan history with optional filters.
    
    Args:
        db: Database session
        limit: Maximum number of results
        offset: Number of results to skip
        status: Optional status filter
        target: Optional target filter
    
    Returns:
        (list of scans, total count)
    """
    try:
        # Build base query
        query = select(ScanResult)
        count_query = select(func.count(ScanResult.id))
        
        # Apply filters
        filters = []
        if status:
            filters.append(ScanResult.status == status)
        if target:
            filters.append(ScanResult.target.like(f"%{target}%"))
        
        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))
        
        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Get paginated results
        query = query.order_by(desc(ScanResult.created_at)).limit(limit).offset(offset)
        result = await db.execute(query)
        scans = result.scalars().all()
        
        return list(scans), total
        
    except SQLAlchemyError as e:
        logger.error(f"Failed to get scan history: {e}")
        return [], 0


# ==================== DELETE ====================

async def delete_scan(
    db: AsyncSession,
    scan_id: str
) -> bool:
    """
    Delete a scan by ID.
    
    Args:
        db: Database session
        scan_id: Scan identifier
    
    Returns:
        True if deleted, False otherwise
    """
    try:
        query = select(ScanResult).where(ScanResult.scan_id == scan_id)
        res = await db.execute(query)
        scan = res.scalar_one_or_none()
        
        if not scan:
            return False
        
        await db.delete(scan)
        await db.commit()
        
        logger.info(f"Deleted scan: {scan_id}")
        return True
        
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Failed to delete scan {scan_id}: {e}")
        return False


async def cleanup_old_scans(
    db: AsyncSession,
    days: Optional[int] = None
) -> int:
    """
    Delete scans older than specified days.
    
    Args:
        db: Database session
        days: Number of days (default from settings)
    
    Returns:
        Number of scans deleted
    """
    if days is None:
        days = settings.SCAN_RETENTION_DAYS
    
    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        query = select(ScanResult).where(ScanResult.created_at < cutoff_date)
        result = await db.execute(query)
        old_scans = result.scalars().all()
        
        count = 0
        for scan in old_scans:
            await db.delete(scan)
            count += 1
        
        await db.commit()
        
        logger.info(f"Cleaned up {count} scans older than {days} days")
        return count
        
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Failed to cleanup old scans: {e}")
        return 0


# ==================== STATISTICS ====================

async def get_scan_statistics(db: AsyncSession) -> dict:
    """
    Get overall scan statistics.
    
    Returns:
        Dictionary with statistics
    """
    try:
        total_query = select(func.count(ScanResult.id))
        total_result = await db.execute(total_query)
        total_scans = total_result.scalar() or 0
        
        # Count by status
        status_counts = {}
        for status in ScanStatus:
            status_query = select(func.count(ScanResult.id)).where(
                ScanResult.status == status.value
            )
            result = await db.execute(status_query)
            status_counts[status.value] = result.scalar() or 0
        
        # Average risk score
        avg_risk_query = select(func.avg(ScanResult.risk_score)).where(
            ScanResult.status == ScanStatus.COMPLETED.value
        )
        avg_result = await db.execute(avg_risk_query)
        avg_risk = avg_result.scalar() or 0.0
        
        return {
            "total_scans": total_scans,
            "status_counts": status_counts,
            "average_risk_score": round(float(avg_risk), 2),
        }
        
    except SQLAlchemyError as e:
        logger.error(f"Failed to get statistics: {e}")
        return {
            "total_scans": 0,
            "status_counts": {},
            "average_risk_score": 0.0,
        }