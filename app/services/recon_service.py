# app/services/recon_service.py
"""
Passive Reconnaissance & OSINT Engine for XenoraSec.
Provides Certificate Transparency log queries, DNS topology mapping,
mail security analysis (SPF/DMARC), ASN enrichment, and passive tech stack fingerprinting.
"""

import asyncio
import httpx
import re
import socket
from datetime import datetime, UTC
from typing import List, Dict, Any, Optional, Set, Tuple
from urllib.parse import urlparse

from app.schemas.recon import (
    SubdomainRecord,
    SubdomainSource,
    DNSRecord,
    DNSRecordType,
    MailSecurityPosture,
    DNSIntelligence,
    TechStackCategory,
    TechStackItem,
    SecurityHeaderCheck,
    SSLInfo,
    TechFingerprint,
    ReconResult,
)
from app.core.logging import get_logger

logger = get_logger(__name__)

DEFAULT_TIMEOUT = 12.0
CRTSH_BASE_URL = "https://crt.sh"
HACKERTARGET_URL = "https://api.hackertarget.com/hostsearch/"
USER_AGENT = "XenoraSec-OSINT/2.1 (Security Assessment Core; +https://github.com/prithvi-01x/XenoraSec)"


class ReconException(Exception):
    """Base exception for passive recon operations."""
    pass


class CrtshClient:
    """
    Certificate Transparency client querying crt.sh API with exponential backoff
    and resilience against upstream timeouts or rate limits.
    """

    def __init__(self, timeout: float = DEFAULT_TIMEOUT, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        }

    async def query_ct_logs(self, domain: str) -> List[Dict[str, Any]]:
        """
        Fetch Certificate Transparency log entries for domain from crt.sh.
        Retries with exponential backoff if crt.sh returns 5xx or times out.
        """
        clean_domain = domain.lower().strip().lstrip(".")
        url = f"{CRTSH_BASE_URL}/?q=%.{clean_domain}&output=json"

        last_error = None
        for attempt in range(1, self.max_retries + 1):
            try:
                async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as client:
                    resp = await client.get(url)
                    if resp.status_code == 200:
                        try:
                            data = resp.json()
                            if isinstance(data, list):
                                logger.info(f"crt.sh returned {len(data)} raw records for {clean_domain}")
                                return data
                        except Exception as parse_err:
                            logger.warning(f"Failed to parse crt.sh JSON: {parse_err}")
                            return []
                    elif resp.status_code in (429, 502, 503, 504):
                        logger.warning(f"crt.sh returned status {resp.status_code}, attempt {attempt}/{self.max_retries}")
                    else:
                        logger.warning(f"crt.sh unexpected status {resp.status_code}")
            except (httpx.TimeoutException, httpx.RequestError) as e:
                last_error = e
                logger.warning(f"crt.sh connection error on attempt {attempt}: {e}")

            if attempt < self.max_retries:
                backoff = (2 ** attempt) * 0.5
                await asyncio.sleep(backoff)

        logger.info(f"crt.sh query completed without direct results for {clean_domain} (last_error: {last_error})")
        return []
