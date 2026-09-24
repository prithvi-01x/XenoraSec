# tests/test_cidr_edge_cases.py

import pytest
from app.core.security import (
    is_cidr_notation,
    validate_cidr_network,
    expand_cidr_target,
    parse_multiple_targets,
    TargetValidationError
)


def test_ipv4_cidr_boundary_prefixes():
    # /32 - exact single IP host
    hosts_32 = expand_cidr_target("192.168.1.100/32")
    assert hosts_32 == ["192.168.1.100"]

    # /31 - RFC 3021 point-to-point link (2 usable hosts)
    hosts_31 = expand_cidr_target("192.168.1.10/31")
    assert hosts_31 == ["192.168.1.10", "192.168.1.11"]

    # /30 - 4 total IPs, 2 usable hosts (.1 and .2)
    hosts_30 = expand_cidr_target("10.0.0.0/30")
    assert len(hosts_30) == 2
    assert hosts_30 == ["10.0.0.1", "10.0.0.2"]

    # /29 - 8 total IPs, 6 usable hosts
    hosts_29 = expand_cidr_target("10.0.0.0/29")
    assert len(hosts_29) == 6

    # /24 - 256 total IPs, 254 usable hosts
    hosts_24 = expand_cidr_target("10.0.0.0/24")
    assert len(hosts_24) == 254
    assert "10.0.0.1" in hosts_24
    assert "10.0.0.254" in hosts_24
    assert "10.0.0.0" not in hosts_24
    assert "10.0.0.255" not in hosts_24


def test_ipv4_cidr_rejection_over_limit():
    # /23 (512 addresses) exceeds /24 limit
    is_valid, err, net = validate_cidr_network("10.0.0.0/23")
    assert is_valid is False
    assert "exceeds maximum allowed size" in err

    # /16 (65536 addresses)
    is_valid, err, net = validate_cidr_network("172.16.0.0/16")
    assert is_valid is False
    assert "exceeds maximum allowed size" in err

    # /8 (16 million addresses)
    is_valid, err, net = validate_cidr_network("10.0.0.0/8")
    assert is_valid is False
    assert "exceeds maximum allowed size" in err


def test_ipv6_cidr_handling():
    # IPv6 notation recognition
    assert is_cidr_notation("2001:db8::/128") is True
    assert is_cidr_notation("fd00::/120") is True

    # Valid IPv6 network /128
    is_valid, err, net = validate_cidr_network("2001:db8::1/128")
    assert is_valid is True

    # IPv6 network /120 is at most 256 addresses
    is_valid, err, net = validate_cidr_network("fd00::/120")
    assert is_valid is True

    # IPv6 network /64 exceeds max 256 hosts cap
    is_valid, err, net = validate_cidr_network("fd00::/64")
    assert is_valid is False
    assert "exceeds maximum allowed size" in err


def test_malformed_cidr_notations():
    # Invalid prefix numbers
    assert validate_cidr_network("192.168.1.1/33")[0] is False
    assert validate_cidr_network("192.168.1.1/-1")[0] is False
    assert validate_cidr_network("192.168.1.1/abc")[0] is False

    # Invalid IP part
    assert validate_cidr_network("999.999.999.999/24")[0] is False
    assert validate_cidr_network("not-an-ip/24")[0] is False

    # Extra slashes
    assert is_cidr_notation("192.168.1.1/24/32") is False


def test_parse_multiple_targets_mixed_delimiters():
    # Tabs, carriage returns, semicolons, commas, spaces
    raw = "  host1.local,\thost2.local\r\nhost3.local ; 1.1.1.1 \n\n 1.1.1.1, host1.local "
    parsed = parse_multiple_targets(raw)
    assert parsed == ["host1.local", "host2.local", "host3.local", "1.1.1.1"]


def test_parse_multiple_targets_batch_size_cap(monkeypatch):
    # Cap batch targets to 5
    from app.core import config
    monkeypatch.setattr(config.settings, "MAX_BATCH_TARGETS", 5)

    raw = "1.1.1.1, 2.2.2.2, 3.3.3.3, 4.4.4.4, 5.5.5.5, 6.6.6.6"
    with pytest.raises(TargetValidationError) as exc:
        parse_multiple_targets(raw, max_targets=5)
    assert "exceeds maximum batch limit" in str(exc.value)
