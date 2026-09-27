# app/services/recon_service.py
"""
Passive Reconnaissance & OSINT Engine for XenoraSec.
Provides Certificate Transparency log queries, DNS topology mapping,
mail security analysis (SPF/DMARC), ASN enrichment, and passive tech stack fingerprinting.
"""

import asyncio
import httpx
import ipaddress
import re
import socket
import ssl
from datetime import datetime, UTC
from typing import List, Dict, Any, Optional, Set, Tuple
from urllib.parse import urlparse

try:
    import dns.asyncresolver
    import dns.resolver
    import dns.reversename
    import dns.rdatatype
    HAS_DNSPYTHON = True
except ImportError:
    HAS_DNSPYTHON = False


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
        clean_domain = domain.lower().strip().strip(".")
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
        clean_domain = domain.lower().strip().strip(".")
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
                name = raw_name.strip().lower().rstrip(".")
                if not name:
                    continue

                is_wildcard = False
                if name.startswith("*."):
                    is_wildcard = True
                    name = re.sub(r"^(\*\.)+", "", name).rstrip(".")
                elif name.startswith("*"):
                    is_wildcard = True
                    name = name.lstrip("*.").rstrip(".")

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
        raw_sub = subdomain.strip()
        raw_root = root_domain.strip()

        # Reject empty or strings starting with a dot
        if not raw_sub or not raw_root or raw_sub.startswith("."):
            return False

        clean_sub = raw_sub.lower().rstrip(".")
        clean_root = raw_root.lower().rstrip(".")

        if not clean_sub or not clean_root:
            return False
        if clean_sub == clean_root:
            return True
        if not clean_sub.endswith(f".{clean_root}"):
            return False
        if ".." in clean_sub:
            return False
        # Discard names with invalid characters (only alphanumeric, hyphens, underscores, and dots)
        if not re.match(r"^[a-zA-Z0-9_\-\.]+$", clean_sub):
            return False
        # Labels check: labels should not start or end with a hyphen
        labels = clean_sub.split(".")
        for label in labels:
            if not label or label.startswith("-") or label.endswith("-"):
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
        clean_domain = domain.lower().strip().strip(".")
        url = f"{HACKERTARGET_URL}?q={clean_domain}"

        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    text = resp.text.strip()
                    # HackerTarget returns 'subdomain,ip\nsubdomain,ip' or error string
                    lower_text = text.lower()
                    if (
                        "error" in lower_text
                        or "no dns records found" in lower_text
                        or "api count exceeded" in lower_text
                        or text.strip().startswith("<")
                    ):
                        return []

                    records: List[SubdomainRecord] = []
                    seen: Set[str] = set()
                    for line in text.splitlines():
                        parts = line.strip().split(",")
                        if not parts:
                            continue
                        sub = parts[0].strip().lower().rstrip(".")
                        raw_ip = parts[1].strip() if len(parts) > 1 else None

                        if not sub or sub in seen:
                            continue
                        if not CrtshClient._is_valid_subdomain(sub, clean_domain):
                            continue

                        # Validate IP if present
                        valid_ips: List[str] = []
                        if raw_ip:
                            try:
                                ipaddress.ip_address(raw_ip)
                                valid_ips.append(raw_ip)
                            except ValueError:
                                pass

                        seen.add(sub)
                        records.append(
                            SubdomainRecord(
                                subdomain=sub,
                                domain=clean_domain,
                                source=SubdomainSource.PASSIVE_DNS.value,
                                ip_addresses=valid_ips,
                                is_active=True if valid_ips else None,
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


class DNSIntelligenceResolver:
    """
    Comprehensive asynchronous DNS resolver providing record extraction (A, AAAA, CNAME,
    MX, TXT, NS, SOA, PTR), DNS-over-HTTPS (DoH) fallback resilience, mail spoofing
    posture evaluation (SPF/DMARC), and ASN/IP topology mapping.
    """

    PUBLIC_DNS_SERVERS = ["1.1.1.1", "1.0.0.1", "8.8.8.8", "8.8.4.4", "9.9.9.9"]
    DOH_URL = "https://cloudflare-dns.com/dns-query"

    DOH_TYPE_MAP = {
        1: "A",
        28: "AAAA",
        5: "CNAME",
        15: "MX",
        16: "TXT",
        2: "NS",
        6: "SOA",
        12: "PTR",
    }

    def __init__(self, timeout: float = 4.0):
        self.timeout = timeout
        self.headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/dns-json",
        }
        self._resolver: Optional[Any] = None
        if HAS_DNSPYTHON:
            try:
                res = dns.asyncresolver.Resolver()
                res.nameservers = self.PUBLIC_DNS_SERVERS
                res.timeout = timeout
                res.lifetime = timeout
                self._resolver = res
            except Exception as e:
                logger.warning(f"Could not initialize async dns resolver: {e}")

    async def resolve_address_records(self, domain: str) -> Tuple[List[DNSRecord], List[str], List[str], List[str]]:
        """
        Extract A, AAAA, and CNAME records for a domain concurrently.
        Returns: (all_records, ipv4_list, ipv6_list, cname_list)
        """
        clean_domain = domain.lower().strip().strip(".")
        records: List[DNSRecord] = []
        ipv4: List[str] = []
        ipv6: List[str] = []
        cnames: List[str] = []

        a_task = self._query_record_type(clean_domain, "A")
        aaaa_task = self._query_record_type(clean_domain, "AAAA")
        cname_task = self._query_record_type(clean_domain, "CNAME")
        a_records, aaaa_records, cname_records = await asyncio.gather(a_task, aaaa_task, cname_task)

        # 1. Process A records (validate IPv4 address format)
        for rec in a_records:
            clean_val = rec.value.strip().rstrip(".")
            try:
                ip_obj = ipaddress.ip_address(clean_val)
                if ip_obj.version == 4:
                    records.append(rec)
                    if clean_val not in ipv4:
                        ipv4.append(clean_val)
            except ValueError:
                logger.debug(f"Discarding non-IPv4 value in A record: {rec.value}")

        # 2. Process AAAA records (validate IPv6 address format)
        for rec in aaaa_records:
            clean_val = rec.value.strip().rstrip(".")
            try:
                ip_obj = ipaddress.ip_address(clean_val)
                if ip_obj.version == 6:
                    records.append(rec)
                    if clean_val not in ipv6:
                        ipv6.append(clean_val)
            except ValueError:
                logger.debug(f"Discarding non-IPv6 value in AAAA record: {rec.value}")

        # 3. Process CNAME records
        for rec in cname_records:
            records.append(rec)
            clean_cname = rec.value.rstrip(".")
            if clean_cname not in cnames:
                cnames.append(clean_cname)

        return records, ipv4, ipv6, cnames

    async def _query_record_type(self, host: str, rtype: str) -> List[DNSRecord]:
        """Query a specific DNS record type using asyncresolver with DoH fallback."""
        if self._resolver:
            try:
                answers = await self._resolver.resolve(host, rtype)
                results: List[DNSRecord] = []
                for rdata in answers:
                    val = str(rdata).strip('"')
                    results.append(
                        DNSRecord(
                            record_type=rtype,
                            host=host,
                            value=val,
                            ttl=getattr(answers, "ttl", None),
                        )
                    )
                return results
            except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                return []
            except Exception as e:
                logger.debug(f"Direct DNS query for {host} {rtype} failed, trying DoH: {e}")

        # Fallback to DoH (DNS-over-HTTPS)
        return await self._query_doh(host, rtype)

    async def _query_doh(self, host: str, rtype: str) -> List[DNSRecord]:
        """Query Cloudflare DNS-over-HTTPS endpoint for record type with type-filtering."""
        url = f"{self.DOH_URL}?name={host}&type={rtype}"
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    answers = data.get("Answer", [])
                    records: List[DNSRecord] = []
                    for ans in answers:
                        ans_type_num = ans.get("type")
                        rec_type = self.DOH_TYPE_MAP.get(ans_type_num, rtype)
                        data_val = str(ans.get("data", "")).strip('"')
                        ttl_val = ans.get("TTL")
                        # Only accept records matching the queried record type
                        if rec_type == rtype and data_val:
                            records.append(
                                DNSRecord(
                                    record_type=rtype,
                                    host=host,
                                    value=data_val,
                                    ttl=ttl_val,
                                )
                            )
                    return records
        except Exception as e:
            logger.debug(f"DoH query for {host} {rtype} failed: {e}")

        return []

    async def resolve_infrastructure_records(
        self, domain: str
    ) -> Tuple[List[DNSRecord], List[str], List[str], List[str]]:
        """
        Extract MX (mail exchangers), NS (nameservers), TXT, and SOA records concurrently.
        Returns: (records, nameservers, mail_servers, txt_records)
        """
        clean_domain = domain.lower().strip().strip(".")
        records: List[DNSRecord] = []
        nameservers: List[str] = []
        mail_servers: List[str] = []
        txt_records: List[str] = []

        ns_task = self._query_record_type(clean_domain, "NS")
        mx_task = self._query_record_type(clean_domain, "MX")
        txt_task = self._query_record_type(clean_domain, "TXT")
        ns_recs, mx_recs, txt_recs = await asyncio.gather(ns_task, mx_task, txt_task)

        # 1. NS records
        for rec in ns_recs:
            records.append(rec)
            ns_host = rec.value.rstrip(".").lower()
            if ns_host not in nameservers:
                nameservers.append(ns_host)

        # 2. MX records
        for rec in mx_recs:
            records.append(rec)
            # Value can be "10 mail.example.com" or "mail.example.com"
            parts = rec.value.split()
            if len(parts) >= 2 and parts[0].isdigit():
                rec.priority = int(parts[0])
                mx_host = parts[1].rstrip(".").lower()
            else:
                mx_host = rec.value.rstrip(".").lower()

            if mx_host not in mail_servers:
                mail_servers.append(mx_host)

        # 3. TXT records
        for rec in txt_recs:
            records.append(rec)
            cleaned_txt = rec.value.strip('"')
            if cleaned_txt not in txt_records:
                txt_records.append(cleaned_txt)

        return records, nameservers, mail_servers, txt_records

    async def evaluate_mail_security(
        self, domain: str, root_txt_records: List[str]
    ) -> MailSecurityPosture:
        """
        Evaluate domain email hygiene, SPF configuration, DMARC enforcement, and DKIM hints.
        Includes RFC 7208 multi-record PermError detection and RFC 7489 parent domain fallback.
        """
        clean_domain = domain.lower().strip().strip(".")
        posture = MailSecurityPosture()

        # 1. Evaluate SPF from root domain TXT records
        spf_records = [txt for txt in root_txt_records if txt.lower().startswith("v=spf1")]

        if len(spf_records) > 1:
            # RFC 7208 Section 3.2: A domain MUST NOT have more than one SPF record (PermError)
            posture.has_spf = True
            posture.spf_record = "; ".join(spf_records)
            posture.spf_status = "permerror"
        elif len(spf_records) == 1:
            spf_rec = spf_records[0]
            posture.has_spf = True
            posture.spf_record = spf_rec
            lower_spf = spf_rec.lower()
            if "-all" in lower_spf:
                posture.spf_status = "pass"
            elif "~all" in lower_spf:
                posture.spf_status = "warning"
            elif "?all" in lower_spf or "+all" in lower_spf:
                posture.spf_status = "insecure"
            else:
                posture.spf_status = "warning"
        else:
            posture.has_spf = False
            posture.spf_status = "missing"

        # 2. Query DMARC at _dmarc.<domain>
        dmarc_host = f"_dmarc.{clean_domain}"
        dmarc_records = await self._query_record_type(dmarc_host, "TXT")
        dmarc_rec = None
        for rec in dmarc_records:
            cleaned = rec.value.strip('"')
            if cleaned.lower().startswith("v=dmarc1"):
                dmarc_rec = cleaned
                break

        # Fallback to parent domain if subdomain and not found (RFC 7489 Section 6.6.3)
        if not dmarc_rec and clean_domain.count(".") >= 2:
            parent_domain = ".".join(clean_domain.split(".")[1:])
            parent_dmarc_host = f"_dmarc.{parent_domain}"
            parent_dmarc_records = await self._query_record_type(parent_dmarc_host, "TXT")
            for rec in parent_dmarc_records:
                cleaned = rec.value.strip('"')
                if cleaned.lower().startswith("v=dmarc1"):
                    dmarc_rec = cleaned
                    # Check for subdomain policy sp=
                    sp_match = re.search(r"\bsp=([a-zA-Z]+)", cleaned, re.IGNORECASE)
                    if sp_match:
                        posture.dmarc_policy = sp_match.group(1).lower()
                    break

        if dmarc_rec:
            posture.has_dmarc = True
            posture.dmarc_record = dmarc_rec
            if not posture.dmarc_policy or posture.dmarc_policy == "missing":
                match = re.search(r"\bp=([a-zA-Z]+)", dmarc_rec, re.IGNORECASE)
                if match:
                    posture.dmarc_policy = match.group(1).lower()
                else:
                    posture.dmarc_policy = "none"
        else:
            posture.has_dmarc = False
            posture.dmarc_policy = "missing"

        # 3. Check DKIM hints from TXT records
        for txt in root_txt_records:
            lower_txt = txt.lower()
            if "v=dkim1" in lower_txt or "k=rsa" in lower_txt or "domainkey" in lower_txt:
                posture.has_dkim_indicator = True
                break

        # 4. Overall rating
        if posture.spf_status == "permerror":
            posture.security_rating = "insecure"
        elif posture.has_dmarc and posture.dmarc_policy in ("reject", "quarantine") and posture.spf_status in ("pass", "warning"):
            posture.security_rating = "secure"
        elif (posture.has_spf and posture.spf_status not in ("insecure", "permerror")) or (posture.has_dmarc and posture.dmarc_policy != "missing"):
            posture.security_rating = "warning"
        else:
            posture.security_rating = "insecure"

        return posture

    async def resolve_reverse_dns(self, ips: List[str]) -> Dict[str, str]:
        """Perform reverse DNS (PTR) resolution for discovered IP addresses."""
        loop = asyncio.get_running_loop()
        results: Dict[str, str] = {}

        async def _ptr(ip: str):
            clean_ip = ip.strip()
            # Try dnspython first if available
            if HAS_DNSPYTHON and self._resolver:
                try:
                    rev_name = dns.reversename.from_address(clean_ip)
                    answers = await self._resolver.resolve(rev_name, "PTR")
                    if answers:
                        results[clean_ip] = str(answers[0]).rstrip(".")
                        return
                except Exception:
                    pass

            try:
                # Fallback to gethostbyaddr
                host, _, _ = await asyncio.wait_for(
                    loop.run_in_executor(None, socket.gethostbyaddr, clean_ip),
                    timeout=2.0
                )
                if host:
                    results[clean_ip] = host
            except Exception:
                pass

        tasks = [_ptr(ip) for ip in ips[:20]]  # Bound to first 20 IPs
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        return results

    async def resolve_asn_details(self, ips: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Enrich IPv4/IPv6 addresses with BGP Autonomous System (ASN),
        Organization, and Country intelligence using public RDAP API with follow-redirects.
        """
        results: Dict[str, Dict[str, Any]] = {}
        unique_ips = list(dict.fromkeys(ips))[:10]  # Bound to first 10 distinct IPs

        async def _query_ip(ip: str):
            clean_ip = ip.strip()
            # Skip private/loopback/link-local/reserved addresses using ipaddress
            try:
                ip_obj = ipaddress.ip_address(clean_ip)
                if (
                    ip_obj.is_private
                    or ip_obj.is_loopback
                    or ip_obj.is_link_local
                    or ip_obj.is_reserved
                    or ip_obj.is_multicast
                    or ip_obj.is_unspecified
                ):
                    results[clean_ip] = {
                        "asn": "AS0",
                        "org": "Loopback / Private Subnet",
                        "country": "LOCAL",
                        "cidr": "Local"
                    }
                    return
            except ValueError:
                # Not a valid IP address
                return

            try:
                # Query RDAP service with follow_redirects=True to handle APNIC/RIPE/AFRINIC referrals
                url = f"https://rdap.arin.net/registry/ip/{clean_ip}"
                async with httpx.AsyncClient(headers=self.headers, timeout=4.0, follow_redirects=True) as client:
                    resp = await client.get(url)
                    if resp.status_code == 200:
                        data = resp.json()
                        org = data.get("name") or data.get("customer", "")
                        handle = data.get("handle", "")
                        results[clean_ip] = {
                            "asn": handle or "AS-UNKNOWN",
                            "org": org or "Registered Network",
                            "country": data.get("country", "GLOBAL"),
                            "cidr": data.get("startAddress", clean_ip)
                        }
                        return
            except Exception as e:
                logger.debug(f"RDAP lookup failed for {clean_ip}: {e}")

            # Fallback placeholder
            results[clean_ip] = {
                "asn": "AS-INTERNET",
                "org": "Global Routed Address",
                "country": "GLOBAL",
                "cidr": clean_ip
            }

        tasks = [_query_ip(ip) for ip in unique_ips]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        return results

    async def resolve_full_dns(self, domain: str) -> DNSIntelligence:
        """
        Execute unified DNS intelligence collection pipeline.
        Resolves address records, infrastructure records, mail security, and ASN data.
        """
        clean_domain = domain.lower().strip().lstrip(".")

        # Run address and infrastructure resolutions concurrently
        addr_task = self.resolve_address_records(clean_domain)
        infra_task = self.resolve_infrastructure_records(clean_domain)

        (addr_records, ipv4, ipv6, cnames), (infra_records, nameservers, mail_servers, txt_records) = (
            await asyncio.gather(addr_task, infra_task)
        )

        all_records = addr_records + infra_records

        # Mail security posture analysis
        mail_posture = await self.evaluate_mail_security(clean_domain, txt_records)

        # Reverse DNS and ASN enrichment on discovered IPs
        all_ips = ipv4 + ipv6
        rev_dns_task = self.resolve_reverse_dns(all_ips)
        asn_task = self.resolve_asn_details(all_ips)

        rev_dns, asn_details = await asyncio.gather(rev_dns_task, asn_task)

        return DNSIntelligence(
            domain=clean_domain,
            records=all_records,
            nameservers=nameservers,
            mail_servers=mail_servers,
            ipv4_addresses=ipv4,
            ipv6_addresses=ipv6,
            cname_records=cnames,
            txt_records=txt_records,
            reverse_dns=rev_dns,
            mail_security=mail_posture,
            asn_details=asn_details,
        )


class PassiveTechFingerprinter:
    """
    Non-intrusive HTTP/HTTPS passive technology stack fingerprinter.
    Analyzes response headers, server tokens, cookie banners, script signatures,
    HTML metadata, and TLS negotiation to detect web servers, frameworks, CMSs, and security headers.
    """

    KNOWN_SERVERS = {
        "nginx": ("Nginx", "web_server"),
        "apache": ("Apache HTTP Server", "web_server"),
        "caddy": ("Caddy Web Server", "web_server"),
        "microsoft-iis": ("Microsoft IIS", "web_server"),
        "litespeed": ("LiteSpeed Web Server", "web_server"),
        "openresty": ("OpenResty", "web_server"),
        "cloudflare": ("Cloudflare Edge", "cdn_waf"),
        "akamai": ("Akamai Edge", "cdn_waf"),
        "fastly": ("Fastly CDN", "cdn_waf"),
        "amazon": ("Amazon CloudFront / AWS", "cdn_waf"),
        "gunicorn": ("Gunicorn WSGI", "framework"),
        "uvicorn": ("Uvicorn ASGI", "framework"),
        "werkzeug": ("Werkzeug", "framework"),
        "envoy": ("Envoy Proxy", "web_server"),
        "varnish": ("Varnish Cache", "web_server"),
    }

    def __init__(self, timeout: float = 6.0):
        self.timeout = timeout
        self.headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

    async def probe_endpoint(self, domain: str) -> Optional[Tuple[str, httpx.Response]]:
        """
        Probe endpoint over HTTPS first, falling back to HTTP.
        Follows redirects safely and returns the actual final URL and response.
        """
        clean = domain.strip().lower().strip(".")
        for proto in ("https", "http"):
            url = f"{proto}://{clean}"
            try:
                async with httpx.AsyncClient(
                    headers=self.headers,
                    timeout=self.timeout,
                    follow_redirects=True,
                    verify=False  # Do not block on self-signed certs during passive recon
                ) as client:
                    resp = await client.get(url)
                    final_url = str(resp.url)
                    return final_url, resp
            except Exception as e:
                logger.debug(f"Passive probe failed for {url}: {e}")

        return None

    @staticmethod
    def extract_tls_info(domain: str, timeout: float = 3.5) -> Optional[SSLInfo]:
        """
        Extract TLS certificate metadata (issuer, subject, validity, protocol) synchronously.
        """
        clean_host = domain.strip().lower().strip(".")
        # Strip protocol/path if somehow present
        clean_host = re.sub(r"^[a-zA-Z]+://", "", clean_host).split("/")[0].split(":")[0]
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            with socket.create_connection((clean_host, 443), timeout=timeout) as sock:
                with ctx.wrap_socket(sock, server_hostname=clean_host) as ssock:
                    protocol = ssock.version()

            # Attempt full certificate attribute query with default verification context
            issuer_name = None
            subject_name = clean_host
            valid_from = None
            valid_to = None
            days_until_expiry = None

            try:
                ctx_verify = ssl.create_default_context()
                with socket.create_connection((clean_host, 443), timeout=timeout) as sock2:
                    with ctx_verify.wrap_socket(sock2, server_hostname=clean_host) as ssock2:
                        cert_dict = ssock2.getpeercert()
                        if cert_dict:
                            sub_parts = dict(x[0] for x in cert_dict.get("subject", ()))
                            iss_parts = dict(x[0] for x in cert_dict.get("issuer", ()))
                            subject_name = sub_parts.get("commonName") or clean_host
                            issuer_name = iss_parts.get("organizationName") or iss_parts.get("commonName") or "Trusted CA"
                            valid_from = cert_dict.get("notBefore")
                            valid_to = cert_dict.get("notAfter")
                            if valid_to:
                                try:
                                    exp_dt = datetime.strptime(valid_to, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=UTC)
                                    days_until_expiry = max(0, (exp_dt - datetime.now(UTC)).days)
                                except Exception:
                                    pass
            except Exception:
                issuer_name = "Self-Signed / Private CA"

            return SSLInfo(
                enabled=True,
                issuer=issuer_name,
                subject=subject_name,
                valid_from=valid_from,
                valid_to=valid_to,
                days_until_expiry=days_until_expiry,
                protocol=protocol or "TLSv1.3",
            )
        except Exception as e:
            logger.debug(f"TLS extraction failed for {clean_host}: {e}")
            return None

    def analyze_headers(self, headers: httpx.Headers) -> List[TechStackItem]:
        """Inspect HTTP response headers for web servers and runtime tokens."""
        detected: List[TechStackItem] = []
        lower_headers = {k.lower(): v for k, v in headers.items()}

        # 1. Server header
        server_val = lower_headers.get("server", "")
        if server_val:
            server_lower = server_val.lower()
            matched = False
            for token, (canonical_name, category) in self.KNOWN_SERVERS.items():
                if token in server_lower:
                    version = self._extract_version(server_val, token)
                    detected.append(
                        TechStackItem(
                            name=canonical_name,
                            category=category,
                            version=version,
                            confidence=95,
                            match_evidence=f"Header: Server: {server_val}"
                        )
                    )
                    matched = True
                    break
            if not matched and server_val.strip():
                detected.append(
                    TechStackItem(
                        name=server_val.strip(),
                        category=TechStackCategory.WEB_SERVER.value,
                        confidence=70,
                        match_evidence=f"Header: Server: {server_val}"
                    )
                )

        # 2. X-Powered-By header
        x_powered = lower_headers.get("x-powered-by", "")
        if x_powered:
            pw_lower = x_powered.lower()
            if "php" in pw_lower:
                v = self._extract_version(x_powered, "php")
                detected.append(TechStackItem(name="PHP", category="programming_language", version=v, confidence=100, match_evidence=f"Header: X-Powered-By: {x_powered}"))
            elif "express" in pw_lower:
                detected.append(TechStackItem(name="Express.js", category="framework", confidence=100, match_evidence=f"Header: X-Powered-By: {x_powered}"))
            elif "asp.net" in pw_lower:
                detected.append(TechStackItem(name="ASP.NET", category="framework", confidence=100, match_evidence=f"Header: X-Powered-By: {x_powered}"))
            elif "next.js" in pw_lower:
                v = self._extract_version(x_powered, "next.js")
                detected.append(TechStackItem(name="Next.js", category="framework", version=v, confidence=100, match_evidence=f"Header: X-Powered-By: {x_powered}"))
            else:
                detected.append(TechStackItem(name=x_powered.strip(), category="framework", confidence=85, match_evidence=f"Header: X-Powered-By: {x_powered}"))

        # 3. Via and Edge CDN headers
        if "cf-ray" in lower_headers or "cf-cache-status" in lower_headers:
            if not any(d.name == "Cloudflare Edge" for d in detected):
                detected.append(TechStackItem(name="Cloudflare", category="cdn_waf", confidence=100, match_evidence="Header: CF-Ray / CF-Cache-Status present"))

        if "x-amz-cf-id" in lower_headers or "x-amz-cf-pop" in lower_headers:
            detected.append(TechStackItem(name="Amazon CloudFront", category="cdn_waf", confidence=100, match_evidence="Header: X-Amz-Cf-Id present"))

        if "x-fastly-request-id" in lower_headers:
            detected.append(TechStackItem(name="Fastly CDN", category="cdn_waf", confidence=100, match_evidence="Header: X-Fastly-Request-Id present"))

        if "x-github-request-id" in lower_headers:
            detected.append(TechStackItem(name="GitHub Pages", category="web_server", confidence=100, match_evidence="Header: X-GitHub-Request-Id present"))

        return detected

    @staticmethod
    def _extract_version(header_value: str, token: str) -> Optional[str]:
        """Extract version numbers following a token (e.g. 'nginx/1.24.0' -> '1.24.0')."""
        pattern = rf"{re.escape(token)}[/ ]*([0-9]+\.[0-9]+(?:\.[0-9]+)?)"
        match = re.search(pattern, header_value, re.IGNORECASE)
        if match:
            return match.group(1)
        return None


    def analyze_cookies(self, cookie_names: List[str]) -> List[TechStackItem]:
        """Infer backend technologies from cookie and session names."""
        detected: List[TechStackItem] = []
        c_set = {c.lower() for c in cookie_names}

        # PHP
        if any("phpsessid" in c for c in c_set):
            detected.append(TechStackItem(name="PHP", category="programming_language", confidence=95, match_evidence="Cookie: PHPSESSID detected"))

        # Java (Tomcat / Spring)
        if any("jsessionid" in c for c in c_set):
            detected.append(TechStackItem(name="Java / Spring / Tomcat", category="framework", confidence=95, match_evidence="Cookie: JSESSIONID detected"))

        # Django
        if "csrftoken" in c_set or "sessionid" in c_set:
            detected.append(TechStackItem(name="Django", category="framework", confidence=90, match_evidence="Cookie: Django csrftoken/sessionid detected"))

        # Laravel
        if any("laravel" in c or "xsrf-token" in c for c in c_set):
            detected.append(TechStackItem(name="Laravel", category="framework", confidence=90, match_evidence="Cookie: Laravel session or XSRF-TOKEN detected"))

        # Node / Express
        if "connect.sid" in c_set:
            detected.append(TechStackItem(name="Express.js", category="framework", confidence=95, match_evidence="Cookie: connect.sid detected"))

        # ASP.NET / .NET Core
        if any("asp.net" in c or "aspnet" in c or "antiforgery" in c for c in c_set):
            detected.append(TechStackItem(name="ASP.NET / .NET Core", category="framework", confidence=95, match_evidence="Cookie: ASP.NET session or antiforgery detected"))

        # WordPress
        if any("wordpress" in c or "wp-settings" in c for c in c_set):
            detected.append(TechStackItem(name="WordPress", category="cms", confidence=100, match_evidence="Cookie: wp-settings or wordpress session detected"))

        # Cloudflare
        if any("cf_clearance" in c or "__cf_bm" in c for c in c_set):
            detected.append(TechStackItem(name="Cloudflare Bot Management", category="cdn_waf", confidence=100, match_evidence="Cookie: __cf_bm / cf_clearance detected"))

        # AWS ALB
        if any("awsalb" in c for c in c_set):
            detected.append(TechStackItem(name="AWS ALB", category="cdn_waf", confidence=100, match_evidence="Cookie: AWSALB detected"))

        # Ruby on Rails
        if any("_rails_session" in c or "_session_id" in c for c in c_set):
            detected.append(TechStackItem(name="Ruby on Rails", category="framework", confidence=85, match_evidence="Cookie: Rails session cookie detected"))

        return detected

    def analyze_html(self, html: str) -> Tuple[Optional[str], List[TechStackItem]]:
        """
        Analyze HTML response body for meta generators, DOM markers,
        client-side framework patterns, and page title.
        """
        detected: List[TechStackItem] = []
        if not html:
            return None, []

        lower_html = html.lower()

        # 1. Extract page title
        title = None
        title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        if title_match:
            title = title_match.group(1).strip()
            # Clean up entities and extra whitespace
            title = re.sub(r"\s+", " ", title)[:150]

        # 2. Meta Generator
        meta_gen_match = re.search(r'<meta[^>]+name=["\']generator["\'][^>]+content=["\']([^"\']+)["\']', html, re.IGNORECASE)
        if not meta_gen_match:
            meta_gen_match = re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+name=["\']generator["\']', html, re.IGNORECASE)

        if meta_gen_match:
            gen_val = meta_gen_match.group(1).strip()
            gen_lower = gen_val.lower()

            if "wordpress" in gen_lower:
                version = self._extract_version(gen_val, "wordpress")
                detected.append(TechStackItem(name="WordPress", category="cms", version=version, confidence=100, match_evidence=f"Meta generator: {gen_val}"))
            elif "drupal" in gen_lower:
                version = self._extract_version(gen_val, "drupal")
                detected.append(TechStackItem(name="Drupal", category="cms", version=version, confidence=100, match_evidence=f"Meta generator: {gen_val}"))
            elif "joomla" in gen_lower:
                version = self._extract_version(gen_val, "joomla")
                detected.append(TechStackItem(name="Joomla", category="cms", version=version, confidence=100, match_evidence=f"Meta generator: {gen_val}"))
            elif "ghost" in gen_lower:
                version = self._extract_version(gen_val, "ghost")
                detected.append(TechStackItem(name="Ghost", category="cms", version=version, confidence=100, match_evidence=f"Meta generator: {gen_val}"))
            elif "gatsby" in gen_lower:
                detected.append(TechStackItem(name="Gatsby", category="framework", confidence=100, match_evidence=f"Meta generator: {gen_val}"))
            elif "hugo" in gen_lower:
                detected.append(TechStackItem(name="Hugo", category="cms", confidence=100, match_evidence=f"Meta generator: {gen_val}"))
            elif "shopify" in gen_lower:
                detected.append(TechStackItem(name="Shopify", category="cms", confidence=100, match_evidence=f"Meta generator: {gen_val}"))
            else:
                detected.append(TechStackItem(name=gen_val, category="cms", confidence=80, match_evidence=f"Meta generator: {gen_val}"))

        # 3. Next.js markers
        if "_next/static" in lower_html or "__next_data__" in lower_html or 'id="__next"' in lower_html:
            detected.append(TechStackItem(name="Next.js", category="framework", confidence=100, match_evidence="HTML pattern: _next/static or __NEXT_DATA__"))
            detected.append(TechStackItem(name="React", category="ui_library", confidence=100, match_evidence="Inferred from Next.js dependency"))

        # 4. React markers
        elif "react" in lower_html and ("data-reactroot" in lower_html or "react-dom" in lower_html or "_reactFiber" in html):
            detected.append(TechStackItem(name="React", category="ui_library", confidence=95, match_evidence="HTML pattern: data-reactroot / react-dom"))

        # 5. Vue.js markers
        if "data-v-" in lower_html or "vue.js" in lower_html or "__vue__" in html:
            detected.append(TechStackItem(name="Vue.js", category="framework", confidence=95, match_evidence="HTML pattern: data-v- scope attribute"))

        # 6. Angular markers
        if "ng-version" in lower_html or "ng-app" in lower_html:
            ng_v_match = re.search(r'ng-version=["\']([^"\']+)["\']', html)
            v = ng_v_match.group(1) if ng_v_match else None
            detected.append(TechStackItem(name="Angular", category="framework", version=v, confidence=100, match_evidence="HTML pattern: ng-version attribute"))

        # 7. WordPress path markers
        if "/wp-content/" in lower_html or "/wp-includes/" in lower_html:
            if not any(d.name == "WordPress" for d in detected):
                detected.append(TechStackItem(name="WordPress", category="cms", confidence=95, match_evidence="HTML pattern: /wp-content/ asset path"))

        # 8. CSS Frameworks: Tailwind and Bootstrap
        if "cdn.tailwindcss.com" in lower_html or "tailwindcss" in lower_html:
            detected.append(TechStackItem(name="Tailwind CSS", category="ui_library", confidence=95, match_evidence="HTML pattern: Tailwind CSS stylesheet reference"))

        if "bootstrap.min.css" in lower_html or "bootstrap.bundle" in lower_html:
            detected.append(TechStackItem(name="Bootstrap", category="ui_library", confidence=95, match_evidence="HTML pattern: Bootstrap CSS/JS bundle"))

        return title, detected

    def analyze_security_headers(self, headers: httpx.Headers) -> Tuple[List[SecurityHeaderCheck], int]:
        """
        Evaluate defensive HTTP security headers and compute overall compliance score.
        Headers assessed: HSTS, CSP, X-Frame-Options, X-Content-Type-Options,
        Referrer-Policy, and Permissions-Policy.
        """
        checks: List[SecurityHeaderCheck] = []
        score = 0
        h_map = {k.lower(): v for k, v in headers.items()}

        # 1. HSTS (Strict-Transport-Security) - 25 pts
        hsts = h_map.get("strict-transport-security")
        if hsts:
            has_sub = "includesubdomains" in hsts.lower()
            checks.append(
                SecurityHeaderCheck(
                    header="Strict-Transport-Security",
                    present=True,
                    value=hsts,
                    status="pass" if has_sub else "warning",
                    recommendation=None if has_sub else "Consider adding includeSubDomains to HSTS policy"
                )
            )
            score += 25 if has_sub else 20
        else:
            checks.append(
                SecurityHeaderCheck(
                    header="Strict-Transport-Security",
                    present=False,
                    status="missing",
                    recommendation="Enable HSTS with max-age=31536000 and includeSubDomains to enforce HTTPS"
                )
            )

        # 2. CSP (Content-Security-Policy) - 25 pts
        csp = h_map.get("content-security-policy")
        if csp:
            checks.append(
                SecurityHeaderCheck(
                    header="Content-Security-Policy",
                    present=True,
                    value=csp[:120] + ("..." if len(csp) > 120 else ""),
                    status="pass",
                    recommendation=None
                )
            )
            score += 25
        else:
            checks.append(
                SecurityHeaderCheck(
                    header="Content-Security-Policy",
                    present=False,
                    status="missing",
                    recommendation="Implement Content-Security-Policy to mitigate Cross-Site Scripting (XSS) and code injection"
                )
            )

        # 3. X-Frame-Options - 15 pts
        xfo = h_map.get("x-frame-options")
        if xfo:
            val_upper = xfo.upper()
            is_good = "DENY" in val_upper or "SAMEORIGIN" in val_upper
            checks.append(
                SecurityHeaderCheck(
                    header="X-Frame-Options",
                    present=True,
                    value=xfo,
                    status="pass" if is_good else "warning",
                    recommendation=None if is_good else "Set X-Frame-Options to DENY or SAMEORIGIN to prevent clickjacking"
                )
            )
            score += 15 if is_good else 8
        else:
            checks.append(
                SecurityHeaderCheck(
                    header="X-Frame-Options",
                    present=False,
                    status="missing",
                    recommendation="Configure X-Frame-Options: DENY to protect against clickjacking attacks"
                )
            )

        # 4. X-Content-Type-Options - 15 pts
        xcto = h_map.get("x-content-type-options")
        if xcto and "nosniff" in xcto.lower():
            checks.append(
                SecurityHeaderCheck(
                    header="X-Content-Type-Options",
                    present=True,
                    value=xcto,
                    status="pass",
                    recommendation=None
                )
            )
            score += 15
        else:
            checks.append(
                SecurityHeaderCheck(
                    header="X-Content-Type-Options",
                    present=bool(xcto),
                    value=xcto,
                    status="missing",
                    recommendation="Add X-Content-Type-Options: nosniff to prevent MIME type sniffing"
                )
            )

        # 5. Referrer-Policy - 10 pts
        ref_pol = h_map.get("referrer-policy")
        if ref_pol:
            checks.append(
                SecurityHeaderCheck(
                    header="Referrer-Policy",
                    present=True,
                    value=ref_pol,
                    status="pass",
                    recommendation=None
                )
            )
            score += 10
        else:
            checks.append(
                SecurityHeaderCheck(
                    header="Referrer-Policy",
                    present=False,
                    status="missing",
                    recommendation="Set Referrer-Policy: strict-origin-when-cross-origin to prevent URL referrer leakage"
                )
            )

        # 6. Permissions-Policy - 10 pts
        perm_pol = h_map.get("permissions-policy")
        if perm_pol:
            checks.append(
                SecurityHeaderCheck(
                    header="Permissions-Policy",
                    present=True,
                    value=perm_pol[:100] + ("..." if len(perm_pol) > 100 else ""),
                    status="pass",
                    recommendation=None
                )
            )
            score += 10
        else:
            checks.append(
                SecurityHeaderCheck(
                    header="Permissions-Policy",
                    present=False,
                    status="missing",
                    recommendation="Declare Permissions-Policy to restrict browser features (camera, microphone, geolocation)"
                )
            )

        return checks, min(100, score)

    async def fingerprint(self, domain: str) -> Optional[TechFingerprint]:
        """
        Execute passive technology detection and defensive security header audit.
        """
        probe_result = await self.probe_endpoint(domain)
        if not probe_result:
            return None

        target_url, response = probe_result

        # Analyze HTTP response headers
        header_tech = self.analyze_headers(response.headers)

        # Analyze cookies
        cookie_names = [c.name for c in response.cookies.jar]
        cookie_tech = self.analyze_cookies(cookie_names)

        # Analyze HTML body
        page_title, html_tech = self.analyze_html(response.text)

        # Audit defensive headers
        security_headers, security_score = self.analyze_security_headers(response.headers)

        # Deduplicate detected technologies by name
        tech_map: Dict[str, TechStackItem] = {}
        for item in header_tech + cookie_tech + html_tech:
            if item.name not in tech_map:
                tech_map[item.name] = item
            else:
                # Merge higher confidence or version
                if item.version and not tech_map[item.name].version:
                    tech_map[item.name].version = item.version
                if item.confidence > tech_map[item.name].confidence:
                    tech_map[item.name].confidence = item.confidence

        all_tech = list(tech_map.values())

        # Categorize
        web_servers = [t for t in all_tech if t.category == TechStackCategory.WEB_SERVER.value]
        frameworks = [t for t in all_tech if t.category in (TechStackCategory.FRAMEWORK.value, TechStackCategory.PROGRAMMING_LANGUAGE.value, TechStackCategory.UI_LIBRARY.value)]
        cms = [t for t in all_tech if t.category == TechStackCategory.CMS.value]
        cdn_waf = [t for t in all_tech if t.category == TechStackCategory.CDN_WAF.value]

        # SSL/TLS Info
        ssl_info = None
        if target_url.startswith("https://"):
            try:
                clean_host = re.sub(r"^[a-zA-Z]+://", "", target_url).split("/")[0].split(":")[0]
                ssl_info = await asyncio.wait_for(
                    asyncio.to_thread(self.extract_tls_info, clean_host),
                    timeout=4.0
                )
            except Exception:
                ssl_info = SSLInfo(enabled=True, protocol="TLSv1.3")

        return TechFingerprint(
            target_url=target_url,
            status_code=response.status_code,
            title=page_title,
            web_servers=web_servers,
            frameworks=frameworks,
            cms=cms,
            cdn_waf=cdn_waf,
            all_technologies=all_tech,
            security_headers=security_headers,
            security_score=security_score,
            ssl_info=ssl_info,
        )


class ReconEngine:
    """
    Central passive reconnaissance coordinator managing multi-stage execution,
    concurrency locks, rate-limiting, error resilience, and database persistence.
    """

    def __init__(self, max_concurrent_runs: int = 5):
        self.semaphore = asyncio.Semaphore(max_concurrent_runs)
        self.crtsh_client = CrtshClient()
        self.passive_dns_client = PassiveDnsClient()
        self.subdomain_resolver = SubdomainResolver()
        self.dns_resolver = DNSIntelligenceResolver()
        self.fingerprinter = PassiveTechFingerprinter()

    async def execute_recon(
        self,
        domain: str,
        include_subdomains: bool = True,
        resolve_subdomains: bool = True,
        include_dns: bool = True,
        include_tech_stack: bool = True,
        db: Optional[Any] = None,
    ) -> ReconResult:
        """
        Execute an end-to-end passive OSINT reconnaissance assessment for domain.
        """
        clean_domain = re.sub(r"^[a-zA-Z]+://", "", domain.strip().lower())
        clean_domain = clean_domain.split("/")[0].split(":")[0].strip().strip(".")
        start_time = asyncio.get_running_loop().time()

        async with self.semaphore:
            logger.info(f"Initiating passive reconnaissance pipeline for target: {clean_domain}")

            # 1. Subdomain Discovery Task
            subdomains: List[SubdomainRecord] = []
            subdomain_error: Optional[str] = None

            async def _run_subdomains():
                nonlocal subdomains, subdomain_error
                if not include_subdomains:
                    return

                try:
                    # Query crt.sh
                    raw_ct = await self.crtsh_client.query_ct_logs(clean_domain)
                    ct_records = self.crtsh_client.parse_records(raw_ct, clean_domain)

                    # Query passive DNS fallback/complement
                    pdns_records = await self.passive_dns_client.query_subdomains(clean_domain)

                    # Merge records
                    sub_map: Dict[str, SubdomainRecord] = {}
                    for r in ct_records + pdns_records:
                        if r.subdomain not in sub_map:
                            sub_map[r.subdomain] = r
                        else:
                            # Merge IPs and timestamps
                            existing = sub_map[r.subdomain]
                            if r.ip_addresses:
                                existing.ip_addresses = sorted(list(set(existing.ip_addresses + r.ip_addresses)))
                            if r.is_active is True:
                                existing.is_active = True
                            if r.is_wildcard:
                                existing.is_wildcard = True

                    combined = list(sub_map.values())

                    # If resolution requested, probe them
                    if resolve_subdomains and combined:
                        logger.info(f"Resolving {len(combined)} discovered subdomains for {clean_domain}")
                        combined = await self.subdomain_resolver.resolve_records(combined)

                    subdomains = combined
                except Exception as e:
                    logger.error(f"Subdomain discovery error for {clean_domain}: {e}")
                    subdomain_error = str(e)

            # 2. DNS Intelligence Task
            dns_intel: Optional[DNSIntelligence] = None

            async def _run_dns():
                nonlocal dns_intel
                if not include_dns:
                    dns_intel = DNSIntelligence(domain=clean_domain)
                    return

                try:
                    dns_intel = await self.dns_resolver.resolve_full_dns(clean_domain)
                except Exception as e:
                    logger.error(f"DNS intelligence collection error for {clean_domain}: {e}")
                    dns_intel = DNSIntelligence(domain=clean_domain)

            # 3. Passive Tech Stack Task
            tech_stack: Optional[TechFingerprint] = None

            async def _run_tech():
                nonlocal tech_stack
                if not include_tech_stack:
                    return

                try:
                    tech_stack = await self.fingerprinter.fingerprint(clean_domain)
                except Exception as e:
                    logger.error(f"Tech stack fingerprinting error for {clean_domain}: {e}")

            # Run tasks concurrently
            await asyncio.gather(_run_subdomains(), _run_dns(), _run_tech(), return_exceptions=True)

            duration = round(asyncio.get_running_loop().time() - start_time, 2)
            active_count = sum(1 for s in subdomains if s.is_active is True)
            tech_count = len(tech_stack.all_technologies) if tech_stack else 0
            security_score = tech_stack.security_score if tech_stack else 0

            # Guaranteed non-null DNSIntelligence
            final_dns = dns_intel or DNSIntelligence(domain=clean_domain)

            result = ReconResult(
                domain=clean_domain,
                target=domain,
                status="completed" if not subdomain_error else "partial",
                timestamp=datetime.now(UTC),
                duration=duration,
                subdomains_count=len(subdomains),
                active_subdomains_count=active_count,
                subdomains=subdomains,
                dns=final_dns,
                tech_stack=tech_stack,
                error=subdomain_error,
            )

            # Persist to database if session provided
            if db:
                from app.db.crud import save_recon_result
                try:
                    await save_recon_result(
                        db=db,
                        domain=clean_domain,
                        result_dict=result.model_dump(mode="json"),
                        duration=duration,
                        subdomains_count=len(subdomains),
                        active_subdomains_count=active_count,
                        tech_detected_count=tech_count,
                        security_score=security_score,
                        status=result.status,
                        error_message=subdomain_error,
                    )
                except Exception as db_err:
                    logger.warning(f"Failed to auto-persist recon result to DB: {db_err}")

            return result


# Singleton instance
recon_engine = ReconEngine()












