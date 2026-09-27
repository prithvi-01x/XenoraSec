# tests/test_recon_crtsh.py

import pytest
from app.services.recon_service import CrtshClient, SubdomainResolver
from app.schemas.recon import SubdomainRecord


def test_crtsh_parse_records_san_and_wildcard():
    client = CrtshClient()
    domain = "example.com"
    raw_sample = [
        {
            "entry_timestamp": "2023-01-10T08:30:00",
            "not_after": "2024-01-10T08:30:00",
            "common_name": "example.com",
            "name_value": "example.com\n*.api.example.com\nvpn.example.com",
        },
        {
            "entry_timestamp": "2023-05-12 10:00:00",
            "not_after": "2024-05-12 10:00:00",
            "common_name": "api.example.com",
            "name_value": "api.example.com\nauth.example.com\nother-domain.net",
        },
    ]

    records = client.parse_records(raw_sample, domain)
    record_map = {r.subdomain: r for r in records}

    # 1. Total subdomains parsed (excluding other-domain.net)
    assert "other-domain.net" not in record_map
    assert "example.com" in record_map
    assert "api.example.com" in record_map
    assert "vpn.example.com" in record_map
    assert "auth.example.com" in record_map

    # 2. Wildcard normalization
    api_rec = record_map["api.example.com"]
    assert api_rec.is_wildcard is True

    # 3. Timestamp merging (earliest entry_timestamp and latest not_after)
    assert api_rec.first_seen is not None
    assert api_rec.last_seen is not None
    assert api_rec.first_seen.year == 2023
    assert api_rec.last_seen.year == 2024


def test_crtsh_scope_validation():
    assert CrtshClient._is_valid_subdomain("sub.example.com", "example.com") is True
    assert CrtshClient._is_valid_subdomain("deep.nest.example.com", "example.com") is True
    assert CrtshClient._is_valid_subdomain("example.com", "example.com") is True
    assert CrtshClient._is_valid_subdomain("notexample.com", "example.com") is False
    assert CrtshClient._is_valid_subdomain("sub.attacker.com", "example.com") is False
    assert CrtshClient._is_valid_subdomain("invalid!char.example.com", "example.com") is False


@pytest.mark.asyncio
async def test_subdomain_resolver_active_check():
    resolver = SubdomainResolver()
    test_records = [
        SubdomainRecord(subdomain="localhost", domain="localhost"),
        SubdomainRecord(subdomain="non-existent-subdomain-123456789.invalid", domain="invalid"),
    ]

    resolved = await resolver.resolve_records(test_records)
    res_map = {r.subdomain: r for r in resolved}

    # localhost should resolve to 127.0.0.1 or ::1
    assert res_map["localhost"].is_active is True
    assert len(res_map["localhost"].ip_addresses) > 0

    # invalid domain should not be active
    assert res_map["non-existent-subdomain-123456789.invalid"].is_active is False
