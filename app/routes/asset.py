# app/routes/asset.py

from fastapi import APIRouter, HTTPException, Depends, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import uuid4
import asyncio

from app.db.database import get_db
from app.db.crud import (
    get_assets,
    get_asset_by_id,
    update_asset,
    delete_asset,
    get_asset_statistics,
    create_scan,
)
from app.schemas.asset import (
    AssetListResponse,
    AssetDetailResponse,
    AssetResponse,
    AssetStatsResponse,
    AssetUpdateRequest,
)
from app.schemas.scan import ScanCreateResponse, ScanStatus, ErrorResponse
from app.core.security import validate_target
from app.core.rate_limit import check_rate_limit
from app.core.logging import get_logger
from app.core.config import settings

logger = get_logger(__name__)

router = APIRouter(prefix="/api/assets", tags=["Asset Inventory"])


@router.get("", response_model=AssetListResponse)
async def list_assets_endpoint(
    limit: int = Query(50, ge=1, le=200, description="Items per page"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    search: Optional[str] = Query(None, description="Search by IP or hostname"),
    asset_type: Optional[str] = Query(None, description="Filter by asset type (ip, domain, url, cidr_host)"),
    status: Optional[str] = Query(None, description="Filter by status (active, inactive, scanned)"),
    criticality: Optional[str] = Query(None, description="Filter by criticality (low, medium, high, critical)"),
    min_risk: Optional[float] = Query(None, ge=0.0, le=10.0, description="Filter by minimum risk score"),
    db: AsyncSession = Depends(get_db),
):
    """List and filter tracked assets in the inventory."""
    items, total = await get_assets(
        db=db,
        limit=limit,
        offset=offset,
        search=search,
        asset_type=asset_type,
        status=status,
        criticality=criticality,
        min_risk=min_risk,
    )
    return AssetListResponse(
        items=[AssetResponse.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/stats", response_model=AssetStatsResponse)
async def get_asset_stats_endpoint(db: AsyncSession = Depends(get_db)):
    """Retrieve aggregated inventory statistics and vulnerability totals."""
    stats = await get_asset_statistics(db)
    return AssetStatsResponse(**stats)


@router.get(
    "/{asset_id}",
    response_model=AssetDetailResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_asset_details_endpoint(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve detailed asset findings including discovered ports and vulnerabilities."""
    asset = await get_asset_by_id(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return AssetDetailResponse.model_validate(asset)


@router.patch(
    "/{asset_id}",
    response_model=AssetResponse,
    responses={404: {"model": ErrorResponse}},
)
async def update_asset_endpoint(
    asset_id: int,
    payload: AssetUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """Update asset metadata (criticality, tags, notes, or operational status)."""
    crit_val = payload.criticality.value if payload.criticality else None
    status_val = payload.status.value if payload.status else None

    asset = await update_asset(
        db=db,
        asset_id=asset_id,
        criticality=crit_val,
        status=status_val,
        tags=payload.tags,
        notes=payload.notes,
    )
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return AssetResponse.model_validate(asset)


@router.delete(
    "/{asset_id}",
    responses={404: {"model": ErrorResponse}},
)
async def delete_asset_endpoint(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Delete an asset and its associated findings from the inventory."""
    success = await delete_asset(db, asset_id)
    if not success:
        raise HTTPException(status_code=404, detail="Asset not found")
    return {"message": "Asset deleted successfully", "asset_id": asset_id}


@router.post(
    "/{asset_id}/scan",
    response_model=ScanCreateResponse,
    dependencies=[Depends(check_rate_limit)],
    responses={404: {"model": ErrorResponse}, 400: {"model": ErrorResponse}},
)
async def scan_asset_endpoint(
    asset_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Trigger an on-demand security scan against a specific asset."""
    from app.routes.scan import _run_and_store_scan, _background_tasks

    asset = await get_asset_by_id(db, asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")

    target = asset.hostname or asset.ip_address

    is_valid, err_msg, metadata = validate_target(
        target,
        allow_private=settings.ALLOW_PRIVATE_IP_SCANNING,
        allow_localhost=settings.ALLOW_LOCALHOST_SCANNING,
    )
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Target validation failed: {err_msg}")

    from app.services.scanner_service import get_scan_queue_info
    queue_info = get_scan_queue_info()
    if queue_info["scans_running"] >= settings.MAX_CONCURRENT_SCANS:
        raise HTTPException(
            status_code=503,
            detail=f"Maximum concurrent scans ({settings.MAX_CONCURRENT_SCANS}) reached. Please try again later."
        )

    scan_id = str(uuid4())
    scan = await create_scan(db, scan_id=scan_id, target=target, scan_profile="quick")
    if not scan:
        raise HTTPException(status_code=500, detail="Failed to initialize scan record")

    task = asyncio.create_task(
        _run_and_store_scan(
            scan_id=scan_id,
            target=target,
            metadata=metadata,
            scan_profile="quick",
            options=None,
        )
    )
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)

    return ScanCreateResponse(
        scan_id=scan_id,
        target=target,
        status=ScanStatus.RUNNING,
        scan_profile="quick",
        message="Asset scan launched successfully",
    )
