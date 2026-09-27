# tests/test_recon_fingerprint.py

import pytest
import httpx
from app.services.recon_service import PassiveTechFingerprinter


def test_fingerprint_headers_detection():
    fingerprinter = PassiveTechFingerprinter()
    headers = httpx.Headers({
        "Server": "nginx/1.24.0",
        "X-Powered-By": "PHP/8.2.4",
        "CF-Ray": "893bc458923a123-IAD",
    })

    detected = fingerprinter.analyze_headers(headers)
    names = {t.name: t for t in detected}

    assert "Nginx" in names
    assert names["Nginx"].version == "1.24.0"
    assert names["Nginx"].category == "web_server"

    assert "PHP" in names
    assert names["PHP"].version == "8.2.4"
    assert names["PHP"].category == "programming_language"

    assert "Cloudflare" in names
    assert names["Cloudflare"].category == "cdn_waf"


def test_fingerprint_cookies_detection():
    fingerprinter = PassiveTechFingerprinter()
    cookies = ["csrftoken", "sessionid", "cf_clearance"]

    detected = fingerprinter.analyze_cookies(cookies)
    names = {t.name: t for t in detected}

    assert "Django" in names
    assert names["Django"].category == "framework"
    assert "Cloudflare Bot Management" in names


def test_fingerprint_html_detection():
    fingerprinter = PassiveTechFingerprinter()
    sample_html = """
    <!DOCTYPE html>
    <html>
      <head>
        <title>Mission Portal - XenoraSec</title>
        <meta name="generator" content="WordPress 6.4.3" />
        <script src="/_next/static/chunks/main.js"></script>
        <link rel="stylesheet" href="https://cdn.tailwindcss.com/tailwind.min.css" />
      </head>
      <body>
        <div id="__next">Hello</div>
      </body>
    </html>
    """

    title, detected = fingerprinter.analyze_html(sample_html)
    assert title == "Mission Portal - XenoraSec"

    names = {t.name: t for t in detected}
    assert "WordPress" in names
    assert names["WordPress"].version == "6.4.3"
    assert names["WordPress"].category == "cms"

    assert "Next.js" in names
    assert "React" in names
    assert "Tailwind CSS" in names


def test_security_headers_audit_and_score():
    fingerprinter = PassiveTechFingerprinter()

    # 1. Hardened headers
    hardened_headers = httpx.Headers({
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
        "Content-Security-Policy": "default-src 'self'",
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=()",
    })

    checks, score = fingerprinter.analyze_security_headers(hardened_headers)
    assert score == 100
    assert all(c.status == "pass" for c in checks)

    # 2. Defenseless headers
    empty_headers = httpx.Headers({})
    checks_empty, score_empty = fingerprinter.analyze_security_headers(empty_headers)
    assert score_empty == 0
    assert all(c.status == "missing" for c in checks_empty)
    assert any("HSTS" in (c.recommendation or "") for c in checks_empty)
