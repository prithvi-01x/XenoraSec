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

    def parse_records(self, raw_records: List[Dict[str, Any]], domain: str) -> List[SubdomainRecord]:
        """
        Parse raw crt.sh records into deduplicated SubdomainRecord models,
        extracting all Subject Alternative Names (SANs), normalizing wildcards,
        and tracking certificate entry timestamps.
        """
        clean_domain = domain.lower().strip().lstrip(".")
        subdomain_map: Dict[str, Dict[str, Any]] = {}

        for entry in raw_records:
            entry_ts = self._parse_iso_date(entry.get("entry_timestamp"))
            not_after = self._parse_iso_date(entry.get("not_after"))

            # Name values can be newline-delimited lists of SANs
            raw_names: List[str] = []
            if "name_value" in entry and entry["name_value"]:
                raw_names.extend(str(entry["name_value"]).split("\n"))
            if "common_name" in entry and entry["common_name"]:
                raw_names.append(str(entry["common_name"]))

            for raw_name in raw_names:
                name = raw_name.strip().lower()
                if not name:
                    continue

                is_wildcard = False
                if name.startswith("*."):
                    is_wildcard = True
                    name = name[2:]

                # Discard invalid characters or foreign domains
                if not self._is_valid_subdomain(name, clean_domain):
                    continue

                if name not in subdomain_map:
                    subdomain_map[name] = {
                        "subdomain": name,
                        "domain": clean_domain,
                        "source": SubdomainSource.CRTSH.value,
                        "is_wildcard": is_wildcard,
                        "first_seen": entry_ts,
                        "last_seen": not_after,
                        "ip_addresses": [],
                        "cnames": [],
                    }
                else:
                    if is_wildcard:
                        subdomain_map[name]["is_wildcard"] = True
                    # Update timestamps to widen the window
                    if entry_ts:
                        existing_first = subdomain_map[name]["first_seen"]
                        if not existing_first or entry_ts < existing_first:
                            subdomain_map[name]["first_seen"] = entry_ts
                    if not_after:
                        existing_last = subdomain_map[name]["last_seen"]
                        if not existing_last or not_after > existing_last:
                            subdomain_map[name]["last_seen"] = not_after

        records = [SubdomainRecord(**data) for data in subdomain_map.values()]
        records.sort(key=lambda x: x.subdomain)
        logger.info(f"Parsed and deduplicated {len(records)} unique subdomains from CT logs for {clean_domain}")
        return records

    @staticmethod
    def _is_valid_subdomain(subdomain: str, root_domain: str) -> bool:
        """Validate that subdomain is within root domain scope and well-formed."""
        if subdomain == root_domain:
            return True
        if not subdomain.endswith(f".{root_domain}"):
            return False
        # Discard names with invalid characters (only alphanumeric, hyphens, and dots)
        if not re.match(r"^[a-zA-Z0-9_\-\.]+$", subdomain):
            return False
        return True

    @staticmethod
    def _parse_iso_date(val: Optional[str]) -> Optional[datetime]:
        """Helper to parse crt.sh timestamp strings."""
        if not val or not isinstance(val, str):
            return None
        # Format can be '2023-08-15T12:00:00' or '2023-08-15 12:00:00'
        cleaned = val.replace("T", " ").split(".")[0].strip()
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(cleaned, fmt)
                return dt.replace(tzinfo=UTC)
            except ValueError:
                continue
        return None


class PassiveDnsClient:
    """
    Secondary passive DNS intelligence provider querying public passive DNS records
    (e.g., HackerTarget hostsearch) as a fallback or complementary source to crt.sh.
    """

    def __init__(self, timeout: float = 8.0):
        self.timeout = timeout
        self.headers = {"User-Agent": USER_AGENT}

    async def query_subdomains(self, domain: str) -> List[SubdomainRecord]:
        """
        Query passive DNS records for subdomains.
        Returns normalized SubdomainRecord instances.
        """
        clean_domain = domain.lower().strip().lstrip(".")
        url = f"{HACKERTARGET_URL}?q={clean_domain}"

        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    text = resp.text.strip()
                    # HackerTarget returns 'subdomain,ip\nsubdomain,ip' or error string
                    if "error" in text.lower() or "no dns records found" in text.lower():
                        return []

                    records: List[SubdomainRecord] = []
                    seen: Set[str] = set()
                    for line in text.splitlines():
                        parts = line.strip().split(",")
                        if not parts:
                            continue
                        sub = parts[0].strip().lower()
                        ip = parts[1].strip() if len(parts) > 1 else None

                        if not sub or sub in seen:
                            continue
                        if not sub.endswith(f".{clean_domain}") and sub != clean_domain:
                            continue

                        seen.add(sub)
                        records.append(
                            SubdomainRecord(
                                subdomain=sub,
                                domain=clean_domain,
                                source=SubdomainSource.PASSIVE_DNS.value,
                                ip_addresses=[ip] if ip else [],
                                is_active=True if ip else None,
                            )
                        )
                    logger.info(f"Passive DNS returned {len(records)} subdomains for {clean_domain}")
                    return records
        except Exception as e:
            logger.warning(f"Passive DNS query failed for {clean_domain}: {e}")

        return []


class SubdomainResolver:
    """
    Asynchronous DNS resolution filter that verifies whether discovered subdomains
    are actively routable and resolves their IPv4 and IPv6 network endpoints.
    """

    def __init__(self, concurrency: int = 25, timeout: float = 4.0):
        self.semaphore = asyncio.Semaphore(concurrency)
        self.timeout = timeout

    async def resolve_records(self, records: List[SubdomainRecord]) -> List[SubdomainRecord]:
        """
        Concurrently probe DNS resolution for a list of SubdomainRecord items.
        Updates is_active flag and ip_addresses in-place.
        """
        tasks = [self._resolve_single(record) for record in records]
        updated_records = await asyncio.gather(*tasks, return_exceptions=False)

        # Sort: Active subdomains first, then alphabetically
        updated_records.sort(key=lambda r: (not (r.is_active is True), r.subdomain))
        return updated_records

    async def _resolve_single(self, record: SubdomainRecord) -> SubdomainRecord:
        """Resolve a single hostname to IP addresses with timeout."""
        async with self.semaphore:
            loop = asyncio.get_running_loop()
            try:
                # Run getaddrinfo in default threadpool to avoid blocking event loop
                addr_info = await asyncio.wait_for(
                    loop.getaddrinfo(
                        record.subdomain,
                        None,
                        family=socket.AF_UNSPEC,
                        type=socket.SOCK_STREAM
                    ),
                    timeout=self.timeout
                )
                ips: Set[str] = set()
                for item in addr_info:
                    sockaddr = item[4]
                    if sockaddr and len(sockaddr) > 0:
                        ip = sockaddr[0]
                        ips.add(ip)

                if ips:
                    record.ip_addresses = sorted(list(ips))
                    record.is_active = True
                else:
                    record.is_active = False

            except (socket.gaierror, TimeoutError, asyncio.TimeoutError):
                record.is_active = False
            except Exception as e:
                logger.debug(f"Resolution error for {record.subdomain}: {e}")
                record.is_active = False

            return record



