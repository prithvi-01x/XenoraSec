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
