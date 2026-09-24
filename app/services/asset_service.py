# app/services/asset_service.py

from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import AsyncSessionLocal
from app.db.models import Asset
from app.db.crud import (
    upsert_asset_from_scan,
    get_assets,
    get_asset_by_id,
    update_asset,
    delete_asset,
    get_asset_statistics
)
from app.core.logging import get_logger

logger = get_logger(__name__)


async def auto_index_scan_findings(
    target: str,
    scan_result: dict,
    risk_score: float
) -> Optional[Asset]:
    """
    Safely indexes scan findings into the Asset Inventory database.
    Operates in its own session to ensure scan completion is never blocked by inventory indexing.
    """
    try:
        async with AsyncSessionLocal() as session:
            asset = await upsert_asset_from_scan(
                db=session,
                target=target,
                scan_result=scan_result,
                risk_score=risk_score
            )
            return asset
    except Exception as e:
        logger.error(f"Failed to auto-index findings for target {target} into Asset Inventory: {e}")
        return None


async def get_inventory_assets(
    db: AsyncSession,
    limit: int = 50,
    offset: int = 0,
    search: Optional[str] = None,
    asset_type: Optional[str] = None,
    status: Optional[str] = None,
    criticality: Optional[str] = None,
    min_risk: Optional[float] = None
) -> Tuple[List[Asset], int]:
    """Fetch paginated assets with search and filter conditions."""
    return await get_assets(
        db=db,
        limit=limit,
        offset=offset,
        search=search,
        asset_type=asset_type,
        status=status,
        criticality=criticality,
        min_risk=min_risk
    )


async def get_single_asset_details(
    db: AsyncSession,
    asset_id: int
) -> Optional[Asset]:
    """Fetch complete asset details with associated ports and vulnerabilities."""
    return await get_asset_by_id(db=db, asset_id=asset_id)


async def modify_asset_metadata(
    db: AsyncSession,
    asset_id: int,
    criticality: Optional[str] = None,
    status: Optional[str] = None,
    tags: Optional[List[str]] = None,
    notes: Optional[str] = None
) -> Optional[Asset]:
    """Update asset metadata such as tags, notes, and operational status."""
    return await update_asset(
        db=db,
        asset_id=asset_id,
        criticality=criticality,
        status=status,
        tags=tags,
        notes=notes
    )


async def remove_asset_from_inventory(
    db: AsyncSession,
    asset_id: int
) -> bool:
    """Delete an asset from the inventory."""
    return await delete_asset(db=db, asset_id=asset_id)


async def get_inventory_summary(db: AsyncSession) -> Dict[str, Any]:
    """Fetch aggregated inventory metrics."""
    return await get_asset_statistics(db=db)
