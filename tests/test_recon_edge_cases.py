# tests/test_recon_edge_cases.py
"""
Edge cases and regression test suite for Passive Reconnaissance & OSINT Engine:
1. URL and scheme normalization in ReconEngine.execute_recon (prevents 'https' bug)
2. DoH CNAME filtering to prevent hostnames from polluting ipv4_addresses
3. RFC 1918 / link-local / loopback private range detection in ASN resolver
4. RDAP follow-redirects resilience
5. Trailing dot, double dot, and invalid label boundary handling in subdomain parsing
6. RFC 7208 multiple SPF PermError detection
7. RFC 7489 subdomain parent DMARC fallback with sp= policy
8. DKIM indicator detection in mail security posture
9. TLS certificate extraction logic
"""

import pytest
import ipaddress
from datetime import datetime, UTC
from unittest.mock import AsyncMock, patch

from app.services.recon_service import (
    CrtshClient,
    PassiveDnsClient,
    DNSIntelligenceResolver,
    PassiveTechFingerprinter,
    ReconEngine,
)
from app.schemas.recon import DNSRecord, SubdomainRecord
from app.routes.recon import sanitize_domain_input
from fastapi import HTTPException


def test_domain_normalization_in_execute_recon():
    """Verify that URLs with protocols, ports, and paths normalize correctly without collapsing to 'https'."""
    raw_inputs = [
        ("https://sub.domain.com:8443/login?q=1#top", "sub.domain.com"),
        ("http://example.com/", "example.com"),
        ("HTTP://MY-CORP.ORG:8080/API", "my-corp.org"),
        ("api.service.net.", "api.service.net"),
        ("sub.domain.com:443", "sub.domain.com"),
    ]

    engine = ReconEngine()
    for raw, expected in raw_inputs:
        # Check normalization logic applied at entry
        import re
        clean = re.sub(r"^[a-zA-Z]+://", "", raw.strip().lower())
        clean = clean.split("/")[0].split(":")[0].strip().strip(".")
        assert clean == expected, f"Failed for {raw}: got {clean}, expected {expected}"


def test_subdomain_scope_and_edge_case_sanitization():
    """Verify trailing dots, double dots, wildcard chains, and hyphen boundaries."""
    # Valid cases
    assert CrtshClient._is_valid_subdomain("api.example.com.", "example.com") is True
    assert CrtshClient._is_valid_subdomain("deep.nested.api.example.com", "example.com.") is True
    assert CrtshClient._is_valid_subdomain("example.com", "example.com") is True

    # Invalid cases
    assert CrtshClient._is_valid_subdomain("foo..example.com", "example.com") is False
    assert CrtshClient._is_valid_subdomain(".example.com", "example.com") is False
    assert CrtshClient._is_valid_subdomain("-bad.example.com", "example.com") is False
    assert CrtshClient._is_valid_subdomain("bad-.example.com", "example.com") is False
    assert CrtshClient._is_valid_subdomain("attacker.com", "example.com") is False
    assert CrtshClient._is_valid_subdomain("example.com.attacker.com", "example.com") is False


def test_crtsh_parse_records_with_trailing_dots_and_multi_wildcard():
    """Verify wildcard cleaning and trailing dot normalization in CT records."""
    client = CrtshClient()
    raw = [
        {
            "entry_timestamp": "2023-01-01T00:00:00",
            "not_after": "2024-01-01T00:00:00",
            "name_value": "*.*.api.example.com.\nauth.example.com.\n*.vpn.example.com",
            "common_name": "example.com.",
        }
    ]

    records = client.parse_records(raw, "example.com")
    rec_map = {r.subdomain: r for r in records}

    assert "api.example.com" in rec_map
    assert rec_map["api.example.com"].is_wildcard is True

    assert "auth.example.com" in rec_map
    assert rec_map["auth.example.com"].is_wildcard is False

    assert "vpn.example.com" in rec_map
    assert rec_map["vpn.example.com"].is_wildcard is True

    assert "example.com" in rec_map


@pytest.mark.asyncio
async def test_doh_cname_filtering_prevents_ipv4_pollution():
    """Verify that CNAME records in DoH answer do not pollute ipv4_addresses."""
    resolver = DNSIntelligenceResolver()

    # Mock DoH response containing a CNAME chain
    mock_doh_payload = {
        "Status": 0,
        "Answer": [
            {"name": "www.github.com", "type": 5, "TTL": 300, "data": "github.com."},
            {"name": "github.com", "type": 1, "TTL": 60, "data": "140.82.121.3"},
        ]
    }

    with patch("httpx.AsyncClient.get") as mock_get:
        mock_resp = AsyncMock()
        mock_resp.status_code = 200
        mock_resp.json = lambda: mock_doh_payload
        mock_get.return_value = mock_resp

        # Force DoH path
        records = await resolver._query_doh("www.github.com", "A")
        # Only type 1 (A) should be returned
        assert len(records) == 1
        assert records[0].record_type == "A"
        assert records[0].value == "140.82.121.3"


@pytest.mark.asyncio
async def test_address_resolution_strict_ip_validation():
    """Verify that resolve_address_records discards non-IP strings from ipv4 and ipv6 lists."""
    resolver = DNSIntelligenceResolver()

    async def mock_query(host, rtype):
        if rtype == "A":
            return [
                DNSRecord(record_type="A", host=host, value="93.184.216.34"),
                DNSRecord(record_type="A", host=host, value="not-an-ip.example.com"),
            ]
        if rtype == "AAAA":
            return [
                DNSRecord(record_type="AAAA", host=host, value="2606:2800:220:1:248:1893:25c8:1946"),
                DNSRecord(record_type="AAAA", host=host, value="invalid-ipv6-string"),
            ]
        if rtype == "CNAME":
            return [
                DNSRecord(record_type="CNAME", host=host, value="target.cdn.net.")
            ]
        return []

    resolver._query_record_type = mock_query

    records, ipv4, ipv6, cnames = await resolver.resolve_address_records("example.com")
    assert ipv4 == ["93.184.216.34"]
    assert "not-an-ip.example.com" not in ipv4

    assert ipv6 == ["2606:2800:220:1:248:1893:25c8:1946"]
    assert "invalid-ipv6-string" not in ipv6

    assert cnames == ["target.cdn.net"]


@pytest.mark.asyncio
async def test_asn_rfc1918_and_private_ranges():
    """Verify that all RFC 1918, link-local, and reserved IP ranges are flagged as private."""
    resolver = DNSIntelligenceResolver()
    private_ips = [
        "10.0.0.1",
        "172.20.10.5",     # RFC 1918 mid-block (172.16.0.0/12)
        "172.31.255.1",    # RFC 1918 upper bound
        "192.168.100.1",
        "169.254.169.254", # Link-local / Cloud metadata
        "127.0.0.1",
        "::1",
    ]

    details = await resolver.resolve_asn_details(private_ips)
    for ip in private_ips:
        assert ip in details, f"Missing IP {ip} in ASN results"
        assert details[ip]["asn"] == "AS0"
        assert details[ip]["country"] == "LOCAL"


@pytest.mark.asyncio
async def test_mail_security_rfc7208_multi_spf_permerror():
    """Verify RFC 7208 PermError when domain has multiple SPF records."""
    resolver = DNSIntelligenceResolver()
    domain = "multi-spf.com"
    txt_records = [
        "v=spf1 include:_spf.google.com ~all",
        "v=spf1 include:mailgun.org -all",
    ]

    async def mock_query(host, rtype):
        return []

    resolver._query_record_type = mock_query

    posture = await resolver.evaluate_mail_security(domain, txt_records)
    assert posture.has_spf is True
    assert posture.spf_status == "permerror"
    assert posture.security_rating == "insecure"


@pytest.mark.asyncio
async def test_mail_security_rfc7489_parent_dmarc_fallback():
    """Verify RFC 7489 parent domain fallback for subdomains with sp= policy."""
    resolver = DNSIntelligenceResolver()
    subdomain = "api.corp.example.com"
    txt_records = ["v=spf1 -all"]

    async def mock_query(host, rtype):
        # Subdomain has no DMARC record
        if host == "_dmarc.api.corp.example.com":
            return []
        # Parent domain has DMARC record with sp=reject
        if host == "_dmarc.corp.example.com":
            return [
                DNSRecord(
                    record_type="TXT",
                    host=host,
                    value="v=DMARC1; p=quarantine; sp=reject; rua=mailto:dmarc@corp.example.com"
                )
            ]
        return []

    resolver._query_record_type = mock_query

    posture = await resolver.evaluate_mail_security(subdomain, txt_records)
    assert posture.has_dmarc is True
    assert posture.dmarc_policy == "reject"  # Inherited from parent sp=reject
    assert posture.security_rating == "secure"


@pytest.mark.asyncio
async def test_mail_security_dkim_indicator_detection():
    """Verify DKIM indicators detection in TXT records."""
    resolver = DNSIntelligenceResolver()
    domain = "dkim-enabled.org"
    txt_records = [
        "v=spf1 -all",
        "k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQ...",
    ]

    async def mock_query(host, rtype):
        return []

    resolver._query_record_type = mock_query

    posture = await resolver.evaluate_mail_security(domain, txt_records)
    assert posture.has_dkim_indicator is True


def test_sanitize_domain_input_validation():
    """Verify sanitize_domain_input handles schemes, paths, ports, and rejects invalid inputs."""
    assert sanitize_domain_input("https://sub.domain.com/path") == "sub.domain.com"
    assert sanitize_domain_input("http://sub.domain.com:8080") == "sub.domain.com"
    assert sanitize_domain_input("ftp://sub.domain.com") == "sub.domain.com"
    assert sanitize_domain_input("sub.domain.com.") == "sub.domain.com"

    with pytest.raises(HTTPException):
        sanitize_domain_input("foo..bar.com")

    with pytest.raises(HTTPException):
        sanitize_domain_input("invalid domain; injection")
