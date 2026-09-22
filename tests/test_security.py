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
