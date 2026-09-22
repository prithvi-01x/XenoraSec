# tests/test_rate_limit.py

import pytest
from unittest.mock import MagicMock
from app.core.rate_limit import RateLimiter
from app.core.config import settings


def test_get_client_ip_direct_without_proxy_trust():
    limiter = RateLimiter()
    request = MagicMock()
    request.client.host = "198.51.100.10"
    request.headers = {
        "X-Forwarded-For": "203.0.113.195, 10.0.0.1",
        "X-Real-IP": "192.0.2.1"
    }

    # When TRUST_PROXY_HEADERS is False, headers are ignored
    settings.TRUST_PROXY_HEADERS = False
    ip = limiter.get_client_ip(request)
    assert ip == "198.51.100.10"


def test_get_client_ip_trusted_proxy_forwarded():
    limiter = RateLimiter()
    request = MagicMock()
    request.client.host = "127.0.0.1"
    request.headers = {
        "X-Forwarded-For": "spoofed.ip.here, 203.0.113.50",
    }

    settings.TRUST_PROXY_HEADERS = True
    settings.TRUSTED_PROXIES = ["127.0.0.1"]
    ip = limiter.get_client_ip(request)
    assert ip == "203.0.113.50"


def test_get_client_ip_untrusted_direct_host():
    limiter = RateLimiter()
    request = MagicMock()
    request.client.host = "198.51.100.99"
    request.headers = {
        "X-Forwarded-For": "203.0.113.50",
    }

    settings.TRUST_PROXY_HEADERS = True
    settings.TRUSTED_PROXIES = ["127.0.0.1"]
    # Direct client is not in TRUSTED_PROXIES, so proxy headers ignored
    ip = limiter.get_client_ip(request)
    assert ip == "198.51.100.99"


def test_rate_limiter_enforcement():
    limiter = RateLimiter()
    settings.RATE_LIMIT_ENABLED = True
    settings.RATE_LIMIT_PER_MINUTE = 3
    client = "192.0.2.42"

    allowed, err = limiter.check_rate_limit(client)
    assert allowed is True

    allowed, err = limiter.check_rate_limit(client)
    assert allowed is True

    allowed, err = limiter.check_rate_limit(client)
    assert allowed is True

    # 4th request exceeds per-minute limit of 3
    allowed, err = limiter.check_rate_limit(client)
    assert allowed is False
    assert "Rate limit exceeded" in err
