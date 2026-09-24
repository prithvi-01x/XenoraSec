# app/db/crud.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_, or_, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List, Tuple
from datetime import datetime, UTC, timedelta

from app.db.models import ScanResult, Asset, AssetPort, AssetVulnerability
from app.schemas.scan import ScanStatus
from app.core.logging import get_logger
from app.core.config import settings
from app.core.security import extract_hostname, resolve_hostname_ips, validate_ip_address

logger = get_logger(__name__)


# ==================== CREATE ====================

async def create_scan(
    db: AsyncSession,
    scan_id: str,
    target: str,
    parent_scan_id: Optional[str] = None,
    scan_profile: Optional[str] = "quick",
    scan_options: Optional[dict] = None,
    batch_id: Optional[str] = None
) -> Optional[ScanResult]:
    """
    Create a new scan record in the database.
    
    Args:
        db: Database session
        scan_id: Unique scan identifier (UUID)
        target: Target hostname/IP/URL
        parent_scan_id: Optional parent scan ID for retries
        scan_profile: Active scan profile ('quick', 'full', 'network', 'custom')
        scan_options: Serialized scan options and overrides
        batch_id: Optional identifier grouping scans in a batch/CIDR run
    
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
            batch_id=batch_id,
            scan_profile=scan_profile or "quick",
            scan_options=scan_options,
        )
        
        db.add(scan)
        await db.commit()
        await db.refresh(scan)
        
        logger.info(f"Created scan: {scan_id} for target: {target} (batch={batch_id})")
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
        if "scan_profile" in result and result["scan_profile"]:
            scan.scan_profile = result["scan_profile"]
        if "scan_options" in result and result["scan_options"] is not None:
            scan.scan_options = result["scan_options"]
        scan.updated_at = datetime.now(UTC)
        
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
        scan.updated_at = datetime.now(UTC)
        
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
            # Escape LIKE wildcards to prevent filter bypass
            # Users shouldn't be able to use % or _ as wildcards
            escaped_target = target.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
            filters.append(ScanResult.target.like(f"%{escaped_target}%", escape='\\'))
        
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
    Delete scans older than specified days using bulk delete.
    
    Args:
        db: Database session
        days: Number of days (default from settings)
    
    Returns:
        Number of scans deleted
    """
    if days is None:
        days = settings.SCAN_RETENTION_DAYS
    
    try:
        cutoff_date = datetime.now(UTC) - timedelta(days=days)
        
        # Bulk delete in a single query - much faster than row-by-row
        stmt = delete(ScanResult).where(ScanResult.created_at < cutoff_date)
        result = await db.execute(stmt)
        await db.commit()
        
        count = result.rowcount
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
        # Fix 11: Single query with GROUP BY instead of one query per status (was N+1)
        total_query = select(func.count(ScanResult.id))
        total_result = await db.execute(total_query)
        total_scans = total_result.scalar() or 0

        # One query to count all statuses at once
        status_query = select(ScanResult.status, func.count(ScanResult.id)).group_by(ScanResult.status)
        status_result = await db.execute(status_query)
        status_counts = {row[0]: row[1] for row in status_result.all()}
        # Ensure all statuses are present even if count is 0
        for status in ScanStatus:
            status_counts.setdefault(status.value, 0)

        # Average risk score for completed scans
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


# ==================== BATCH SCAN QUERIES ====================

async def get_scans_by_batch(
    db: AsyncSession,
    batch_id: str
) -> List[ScanResult]:
    """Retrieve all scans belonging to a specific batch ID."""
    try:
        query = select(ScanResult).where(ScanResult.batch_id == batch_id).order_by(ScanResult.created_at.asc())
        result = await db.execute(query)
        return list(result.scalars().all())
    except SQLAlchemyError as e:
        logger.error(f"Failed to get scans for batch {batch_id}: {e}")
        return []


# ==================== ASSET INVENTORY CRUD ====================

async def upsert_asset_from_scan(
    db: AsyncSession,
    target: str,
    scan_result: dict,
    risk_score: float
) -> Optional[Asset]:
    """
    Ingest scan results into the Asset Inventory.
    Creates or updates the asset, associated open ports, and discovered vulnerabilities.
    """
    try:
        hostname, scheme = extract_hostname(target)
        is_ip, _ = validate_ip_address(hostname)

        if is_ip:
            ip_addr = hostname
            asset_host = None
            asset_type = "ip"
        else:
            asset_host = hostname
            resolved = resolve_hostname_ips(hostname)
            ip_addr = resolved[0] if resolved else hostname
            asset_type = "url" if scheme else "domain"

        # Find existing asset by IP or hostname
        stmt = select(Asset).where(
            or_(
                Asset.ip_address == ip_addr,
                and_(Asset.hostname.is_not(None), Asset.hostname == asset_host) if asset_host else False
            )
        )
        res = await db.execute(stmt)
        asset = res.scalar_one_or_none()

        if not asset:
            asset = Asset(
                ip_address=ip_addr,
                hostname=asset_host,
                asset_type=asset_type,
                status="active",
                criticality="medium",
                risk_score=risk_score,
                last_scanned_at=datetime.now(UTC)
            )
            db.add(asset)
            await db.flush()
        else:
            asset.risk_score = max(asset.risk_score, risk_score)
            asset.last_scanned_at = datetime.now(UTC)
            if asset_host and not asset.hostname:
                asset.hostname = asset_host
            if asset.asset_type == "ip" and asset_type != "ip":
                asset.asset_type = asset_type

        # Upsert discovered ports
        nmap_ports = scan_result.get("nmap", {}).get("ports", [])
        if isinstance(nmap_ports, list):
            for p in nmap_ports:
                if isinstance(p, dict) and "port" in p:
                    port_num = p["port"]
                    proto = p.get("protocol", "tcp")
                    p_query = select(AssetPort).where(
                        and_(AssetPort.asset_id == asset.id, AssetPort.port == port_num, AssetPort.protocol == proto)
                    )
                    p_res = await db.execute(p_query)
                    port_rec = p_res.scalar_one_or_none()
                    if port_rec:
                        port_rec.service = p.get("service") or port_rec.service
                        port_rec.product = p.get("product") or port_rec.product
                        port_rec.version = p.get("version") or port_rec.version
                        port_rec.last_seen = datetime.now(UTC)
                    else:
                        new_port = AssetPort(
                            asset_id=asset.id,
                            port=port_num,
                            protocol=proto,
                            service=p.get("service"),
                            product=p.get("product"),
                            version=p.get("version"),
                            last_seen=datetime.now(UTC)
                        )
                        db.add(new_port)

        # Upsert discovered vulnerabilities
        nuclei_vulns = scan_result.get("nuclei", {}).get("vulnerabilities", [])
        if isinstance(nuclei_vulns, list):
            for v in nuclei_vulns:
                if isinstance(v, dict):
                    v_name = v.get("name") or "Unknown Finding"
                    t_id = v.get("template_id")
                    v_query = select(AssetVulnerability).where(
                        and_(AssetVulnerability.asset_id == asset.id, AssetVulnerability.template_id == t_id, AssetVulnerability.name == v_name)
                    )
                    v_res = await db.execute(v_query)
                    vuln_rec = v_res.scalar_one_or_none()
                    if vuln_rec:
                        vuln_rec.severity = v.get("severity") or vuln_rec.severity
                        vuln_rec.cve = v.get("cve") or vuln_rec.cve
                        vuln_rec.cvss = v.get("cvss") or vuln_rec.cvss
                        vuln_rec.matched_at = v.get("matched_at") or vuln_rec.matched_at
                        vuln_rec.last_seen = datetime.now(UTC)
                        vuln_rec.status = "open"
                    else:
                        new_vuln = AssetVulnerability(
                            asset_id=asset.id,
                            template_id=t_id,
                            name=v_name,
                            severity=str(v.get("severity", "info")).lower(),
                            cve=v.get("cve"),
                            cvss=v.get("cvss"),
                            matched_at=v.get("matched_at"),
                            status="open",
                            first_seen=datetime.now(UTC),
                            last_seen=datetime.now(UTC)
                        )
                        db.add(new_vuln)

        await db.flush()

        # Update aggregated statistics on the Asset row
        ports_count_res = await db.execute(select(func.count(AssetPort.id)).where(AssetPort.asset_id == asset.id))
        asset.open_ports_count = ports_count_res.scalar() or 0

        vulns_count_res = await db.execute(
            select(func.count(AssetVulnerability.id)).where(
                and_(AssetVulnerability.asset_id == asset.id, AssetVulnerability.status == "open")
            )
        )
        asset.vulnerabilities_count = vulns_count_res.scalar() or 0

        sev_query = select(AssetVulnerability.severity, func.count(AssetVulnerability.id)).where(
            and_(AssetVulnerability.asset_id == asset.id, AssetVulnerability.status == "open")
        ).group_by(AssetVulnerability.severity)
        sev_res = await db.execute(sev_query)
        sev_counts = {row[0].lower(): row[1] for row in sev_res.all()}

        asset.critical_count = sev_counts.get("critical", 0)
        asset.high_count = sev_counts.get("high", 0)
        asset.medium_count = sev_counts.get("medium", 0)
        asset.low_count = sev_counts.get("low", 0)

        # Elevate criticality rating based on findings
        if asset.critical_count > 0:
            asset.criticality = "critical"
        elif asset.high_count > 0:
            asset.criticality = "high"
        elif asset.medium_count > 0:
            asset.criticality = "medium"

        await db.commit()
        await db.refresh(asset)
        logger.info(f"Asset indexed: {asset.ip_address} (host={asset.hostname}, vulns={asset.vulnerabilities_count})")
        return asset

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Failed to upsert asset from scan: {e}")
        return None


async def get_assets(
    db: AsyncSession,
    limit: int = 50,
    offset: int = 0,
    search: Optional[str] = None,
    asset_type: Optional[str] = None,
    status: Optional[str] = None,
    criticality: Optional[str] = None,
    min_risk: Optional[float] = None
) -> Tuple[List[Asset], int]:
    """Retrieve filtered and paginated assets."""
    try:
        query = select(Asset)
        count_query = select(func.count(Asset.id))

        filters = []
        if search:
            escaped = search.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
            filters.append(
                or_(
                    Asset.ip_address.like(f"%{escaped}%", escape='\\'),
                    Asset.hostname.like(f"%{escaped}%", escape='\\')
                )
            )
        if asset_type:
            filters.append(Asset.asset_type == asset_type)
        if status:
            filters.append(Asset.status == status)
        if criticality:
            filters.append(Asset.criticality == criticality)
        if min_risk is not None:
            filters.append(Asset.risk_score >= min_risk)

        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))

        total_res = await db.execute(count_query)
        total = total_res.scalar() or 0

        query = query.order_by(desc(Asset.risk_score), desc(Asset.updated_at)).limit(limit).offset(offset)
        result = await db.execute(query)
        assets = result.scalars().all()

        return list(assets), total

    except SQLAlchemyError as e:
        logger.error(f"Failed to get assets: {e}")
        return [], 0


async def get_asset_by_id(
    db: AsyncSession,
    asset_id: int
) -> Optional[Asset]:
    """Retrieve single asset by ID with pre-loaded ports and vulnerabilities."""
    try:
        query = (
            select(Asset)
            .options(selectinload(Asset.ports), selectinload(Asset.vulnerabilities))
            .where(Asset.id == asset_id)
        )
        res = await db.execute(query)
        return res.scalar_one_or_none()
    except SQLAlchemyError as e:
        logger.error(f"Failed to get asset {asset_id}: {e}")
        return None


async def update_asset(
    db: AsyncSession,
    asset_id: int,
    criticality: Optional[str] = None,
    status: Optional[str] = None,
    tags: Optional[List[str]] = None,
    notes: Optional[str] = None
) -> Optional[Asset]:
    """Update metadata for an asset."""
    try:
        asset = await get_asset_by_id(db, asset_id)
        if not asset:
            return None

        if criticality:
            asset.criticality = criticality
        if status:
            asset.status = status
        if tags is not None:
            asset.tags = tags
        if notes is not None:
            asset.notes = notes

        asset.updated_at = datetime.now(UTC)
        await db.commit()
        await db.refresh(asset)
        return asset

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Failed to update asset {asset_id}: {e}")
        return None


async def delete_asset(
    db: AsyncSession,
    asset_id: int
) -> bool:
    """Delete an asset and cascade delete associated ports and vulnerabilities."""
    try:
        asset = await get_asset_by_id(db, asset_id)
        if not asset:
            return False

        await db.delete(asset)
        await db.commit()
        return True

    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(f"Failed to delete asset {asset_id}: {e}")
        return False


async def get_asset_statistics(db: AsyncSession) -> dict:
    """Compute aggregated metrics across all assets in the inventory."""
    try:
        total_assets = (await db.execute(select(func.count(Asset.id)))).scalar() or 0
        active_assets = (
            await db.execute(select(func.count(Asset.id)).where(Asset.status == "active"))
        ).scalar() or 0
        critical_risk = (
            await db.execute(select(func.count(Asset.id)).where(Asset.risk_score >= 7.0))
        ).scalar() or 0

        total_ports = (await db.execute(select(func.count(AssetPort.id)))).scalar() or 0
        total_vulns = (
            await db.execute(select(func.count(AssetVulnerability.id)).where(AssetVulnerability.status == "open"))
        ).scalar() or 0

        type_res = await db.execute(select(Asset.asset_type, func.count(Asset.id)).group_by(Asset.asset_type))
        type_dist = {row[0]: row[1] for row in type_res.all()}

        crit_res = await db.execute(select(Asset.criticality, func.count(Asset.id)).group_by(Asset.criticality))
        crit_dist = {row[0]: row[1] for row in crit_res.all()}

        return {
            "total_assets": total_assets,
            "active_assets": active_assets,
            "critical_risk_assets": critical_risk,
            "total_open_ports": total_ports,
            "total_vulnerabilities": total_vulns,
            "asset_type_distribution": type_dist,
            "criticality_distribution": crit_dist,
        }
    except SQLAlchemyError as e:
        logger.error(f"Failed to compute asset statistics: {e}")
        return {
            "total_assets": 0,
            "active_assets": 0,
            "critical_risk_assets": 0,
            "total_open_ports": 0,
            "total_vulnerabilities": 0,
            "asset_type_distribution": {},
            "criticality_distribution": {},
        }