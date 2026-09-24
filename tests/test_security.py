# tests/test_security.py

import pytest
from app.core.security import (
    validate_target,
    is_private_ip,
    is_loopback_ip,
    extract_hostname,
    resolve_hostname_ips
)


def test_is_loopback_and_private():
    assert is_loopback_ip("127.0.0.1") is True
    assert is_loopback_ip("127.0.1.1") is True
    assert is_loopback_ip("::1") is True
    assert is_loopback_ip("0.0.0.0") is True
    assert is_loopback_ip("8.8.8.8") is False

    assert is_private_ip("192.168.1.1") is True
    assert is_private_ip("10.0.0.5") is True
    assert is_private_ip("172.16.0.1") is True
    assert is_private_ip("169.254.169.254") is True
    assert is_private_ip("8.8.8.8") is False


def test_localhost_blocked_by_default():
    # Direct localhost string
    is_valid, err, meta = validate_target("localhost", allow_localhost=False)
    assert is_valid is False
    assert "localhost is not allowed" in err

    # Localhost URL
    is_valid, err, meta = validate_target("http://localhost:8000", allow_localhost=False)
    assert is_valid is False
    assert "localhost is not allowed" in err

    # 127.0.0.1 IP
    is_valid, err, meta = validate_target("127.0.0.1", allow_localhost=False)
    assert is_valid is False
    assert "localhost is not allowed" in err


def test_localhost_allowed_when_flag_enabled():
    is_valid, err, meta = validate_target("localhost", allow_localhost=True)
    assert is_valid is True
    assert meta["is_private"] is True


def test_private_ip_blocked():
    is_valid, err, meta = validate_target("192.168.1.100", allow_private=False)
    assert is_valid is False
    assert "private IP" in err

    is_valid, err, meta = validate_target("10.10.10.10", allow_private=False)
    assert is_valid is False
    assert "private IP" in err


def test_dns_resolution_private_ip_blocked(monkeypatch):
    # Mock DNS resolution returning private IP for a domain
    monkeypatch.setattr("app.core.security.resolve_hostname_ips", lambda h: ["192.168.1.50"])
    
    is_valid, err, meta = validate_target("internal-fake-test.com", allow_private=False)
    assert is_valid is False
    assert "resolves to private/internal IP" in err


def test_valid_public_domain(monkeypatch):
    # Mock DNS resolution returning public IP
    monkeypatch.setattr("app.core.security.resolve_hostname_ips", lambda h: ["93.184.216.34"])
    
    is_valid, err, meta = validate_target("example.com", allow_private=False, allow_localhost=False)
    assert is_valid is True
    assert meta["hostname"] == "example.com"
    assert "93.184.216.34" in meta["resolved_ips"]


def test_uppercase_url_scheme(monkeypatch):
    from app.core.security import prepare_nmap_target, prepare_nuclei_target
    monkeypatch.setattr("app.core.security.resolve_hostname_ips", lambda h: ["93.184.216.34"])

    is_valid, err, meta = validate_target("HTTP://example.com", allow_private=False, allow_localhost=False)
    assert is_valid is True
    assert meta["hostname"] == "example.com"
    assert meta["scheme"] == "http"
    assert prepare_nmap_target("HTTP://example.com", meta) == "example.com"
    assert prepare_nuclei_target("HTTP://example.com", meta) == "http://example.com"


def test_url_with_custom_port_and_path(monkeypatch):
    from app.core.security import prepare_nuclei_target, prepare_nmap_target
    monkeypatch.setattr("app.core.security.resolve_hostname_ips", lambda h: ["93.184.216.34"])

    target = "https://example.com:8443/api/v1"
    is_valid, err, meta = validate_target(target, allow_private=False, allow_localhost=False)
    assert is_valid is True
    assert meta["hostname"] == "example.com"
    assert prepare_nmap_target(target, meta) == "example.com"
    assert prepare_nuclei_target(target, meta) == "https://example.com:8443/api/v1"


def test_bracketed_ipv6_loopback():
    is_valid, err, meta = validate_target("[::1]", allow_localhost=False)
    assert is_valid is False
    assert "localhost is not allowed" in err

    is_valid, err, meta = validate_target("[::1]", allow_localhost=True)
    assert is_valid is True
    assert meta["hostname"] == "::1"


def test_cidr_helpers():
    from app.core.security import (
        is_cidr_notation,
        validate_cidr_network,
        expand_cidr_target,
        parse_multiple_targets,
        TargetValidationError,
    )

    assert is_cidr_notation("192.168.1.0/28") is True
    assert is_cidr_notation("10.0.0.1/32") is True
    assert is_cidr_notation("example.com/api") is False
    assert is_cidr_notation("192.168.1.1") is False

    # Valid network
    is_valid, err, net = validate_cidr_network("192.168.1.0/28")
    assert is_valid is True
    assert net is not None

    # Oversized network (/16 is larger than allowed /24)
    is_valid, err, net = validate_cidr_network("10.0.0.0/16")
    assert is_valid is False
    assert "exceeds maximum allowed size" in err

    # Malformed CIDR
    is_valid, err, net = validate_cidr_network("invalid/24")
    assert is_valid is False
    assert "Invalid CIDR" in err

    # Expansion of /28 (16 IPs total, 14 usable hosts)
    hosts = expand_cidr_target("192.168.1.0/28")
    assert len(hosts) == 14
    assert "192.168.1.1" in hosts
    assert "192.168.1.14" in hosts
    assert "192.168.1.0" not in hosts
    assert "192.168.1.15" not in hosts

    # /32 single host
    hosts_32 = expand_cidr_target("192.168.1.50/32")
    assert hosts_32 == ["192.168.1.50"]


def test_parse_multiple_targets():
    from app.core.security import parse_multiple_targets

    raw = "example.com, 1.1.1.1\n8.8.8.8; 1.1.1.1"
    parsed = parse_multiple_targets(raw)
    assert parsed == ["example.com", "1.1.1.1", "8.8.8.8"]

    # Multi-target with CIDR expansion
    raw_with_cidr = "192.168.1.0/30\n8.8.8.8"
    parsed_cidr = parse_multiple_targets(raw_with_cidr)
    # /30 has 2 usable hosts (.1 and .2)
    assert parsed_cidr == ["192.168.1.1", "192.168.1.2", "8.8.8.8"]


def test_validate_target_cidr_policies():
    # Private CIDR blocked by default
    is_valid, err, meta = validate_target("192.168.1.0/28", allow_private=False)
    assert is_valid is False
    assert "private CIDR subnet" in err

    # Private CIDR allowed when flag enabled
    is_valid, err, meta = validate_target("192.168.1.0/28", allow_private=True)
    assert is_valid is True
    assert meta["is_cidr"] is True
    assert len(meta["cidr_hosts"]) == 14

    # Loopback CIDR blocked when allow_localhost=False
    is_valid, err, meta = validate_target("127.0.0.0/28", allow_localhost=False)
    assert is_valid is False
    assert "localhost subnet" in err

    # Oversized CIDR blocked
    is_valid, err, meta = validate_target("10.0.0.0/16", allow_private=True)
    assert is_valid is False
    assert "exceeds maximum allowed size" in err


