# tests/test_recon_dns.py

import pytest
from app.services.recon_service import DNSIntelligenceResolver
from app.schemas.recon import DNSRecord


@pytest.mark.asyncio
async def test_mail_security_evaluation_secure():
    resolver = DNSIntelligenceResolver()
    domain = "secure-corp.com"
    txt_records = [
        "v=spf1 include:_spf.google.com -all",
        "google-site-verification=abc123xyz"
    ]

    # Mock query to return strong DMARC
    async def mock_query(host, rtype):
        if "_dmarc" in host and rtype == "TXT":
            return [DNSRecord(record_type="TXT", host=host, value="v=DMARC1; p=reject; rua=mailto:dmarc@secure-corp.com")]
        return []

    resolver._query_record_type = mock_query

    posture = await resolver.evaluate_mail_security(domain, txt_records)
    assert posture.has_spf is True
    assert posture.spf_status == "pass"
    assert posture.has_dmarc is True
    assert posture.dmarc_policy == "reject"
    assert posture.security_rating == "secure"


@pytest.mark.asyncio
async def test_mail_security_evaluation_weak_and_missing():
    resolver = DNSIntelligenceResolver()
    domain = "insecure-corp.com"

    # Insecure with +all and missing DMARC
    txt_records = ["v=spf1 +all"]

    async def mock_empty_query(host, rtype):
        return []

    resolver._query_record_type = mock_empty_query

    posture = await resolver.evaluate_mail_security(domain, txt_records)
    assert posture.has_spf is True
    assert posture.spf_status == "insecure"
    assert posture.has_dmarc is False
    assert posture.dmarc_policy == "missing"
    assert posture.security_rating == "insecure"


@pytest.mark.asyncio
async def test_reverse_dns_and_asn_local_handling():
    resolver = DNSIntelligenceResolver()
    test_ips = ["127.0.0.1", "10.0.0.1"]

    rev_dns = await resolver.resolve_reverse_dns(test_ips)
    assert isinstance(rev_dns, dict)
    # 127.0.0.1 typically maps to localhost
    if "127.0.0.1" in rev_dns:
        assert "localhost" in rev_dns["127.0.0.1"].lower()

    asn_details = await resolver.resolve_asn_details(test_ips)
    assert "127.0.0.1" in asn_details
    assert asn_details["127.0.0.1"]["asn"] == "AS0"
    assert "Loopback" in asn_details["127.0.0.1"]["org"]
