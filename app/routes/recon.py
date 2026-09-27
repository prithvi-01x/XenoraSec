# app/routes/recon.py
"""
REST API endpoints for Passive Reconnaissance, Certificate Transparency discovery,
DNS intelligence topology, tech stack fingerprinting, and Asset Inventory sync.
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import re

from app.db.database import get_db
from app.db.crud import (
    get_latest_recon_by_domain,
    get_recon_history,
    import_recon_subdomains_to_assets,
)
from app.schemas.recon import (
    ReconRequest,
    ReconResult,
    ReconHistoryResponse,
    ReconHistoryItem,
    SubdomainImportRequest,
    SubdomainImportResponse,
)
from app.schemas.scan import ErrorResponse
from app.services.recon_service import recon_engine
from app.core.rate_limit import check_rate_limit
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/recon", tags=["Passive Reconnaissance & OSINT"])


def sanitize_domain_input(domain_str: str) -> str:
    """Normalize and validate domain format for passive recon."""
    cleaned = domain_str.strip().lower()
    # Strip protocols if user pasted a URL
    cleaned = re.sub(r"^https?://", "", cleaned)
    # Strip paths, ports, query strings
    cleaned = cleaned.split("/")[0].split(":")[0].strip().rstrip(".")
    if not cleaned or not re.match(r"^[a-zA-Z0-9_\-\.]+$", cleaned):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid target domain format: '{domain_str}'"
        )
    return cleaned


@router.post(
    "",
    response_model=ReconResult,
    dependencies=[Depends(check_rate_limit)],
    responses={
        400: {"model": ErrorResponse, "description": "Invalid domain specification"},
        500: {"model": ErrorResponse, "description": "Recon engine failure"},
    },
)
async def execute_recon_endpoint(
    payload: ReconRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Launch on-demand passive reconnaissance assessment against target domain.
    Executes Certificate Transparency log queries, DNS topology mapping,
    SPF/DMARC mail verification, and non-intrusive tech stack fingerprinting.
    """
    target_domain = sanitize_domain_input(payload.domain)
    logger.info(f"API request: Execute passive recon for domain: {target_domain}")

    try:
        result = await recon_engine.execute_recon(
            domain=target_domain,
            include_subdomains=payload.include_subdomains,
            resolve_subdomains=payload.resolve_subdomains,
            include_dns=payload.include_dns,
            include_tech_stack=payload.include_tech_stack,
            db=db,
        )
        return result
    except Exception as e:
        logger.error(f"Passive recon execution error for {target_domain}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Passive recon assessment failed: {str(e)}"
        )


@router.get(
    "/history",
    response_model=ReconHistoryResponse,
    description="Retrieve paginated history of passive reconnaissance assessments.",
)
async def get_recon_history_endpoint(
    limit: int = Query(50, ge=1, le=200, description="Page size"),
    offset: int = Query(0, ge=0, description="Offset"),
    domain: Optional[str] = Query(None, description="Filter by domain keyword"),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve historical recon assessment records with pagination."""
    records, total = await get_recon_history(db=db, limit=limit, offset=offset, domain=domain)

    items = [
        ReconHistoryItem(
            id=r.id,
            domain=r.domain,
            status=r.status,
            created_at=r.created_at,
            duration=r.duration,
            subdomains_count=r.subdomains_count,
            active_subdomains_count=r.active_subdomains_count,
            tech_detected_count=r.tech_detected_count,
            security_score=r.security_score,
        )
        for r in records
    ]
    return ReconHistoryResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{domain}",
    response_model=ReconResult,
    responses={
        404: {"model": ErrorResponse, "description": "No prior recon record found for domain"}
    },
)
async def get_domain_recon_endpoint(
    domain: str,
    db: AsyncSession = Depends(get_db),
):
    """Retrieve the latest cached passive recon assessment result for domain."""
    cleaned = sanitize_domain_input(domain)
    record = await get_latest_recon_by_domain(db, cleaned)

    if not record or not record.result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No passive reconnaissance record found for '{cleaned}'. Run a scan first."
        )

    try:
        return ReconResult.model_validate(record.result)
    except Exception as e:
        logger.error(f"Failed to parse stored recon result for {cleaned}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deserialize stored reconnaissance result"
        )

