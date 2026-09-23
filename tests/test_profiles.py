# tests/test_profiles.py

import pytest
from app.services.profile_service import (
    get_available_profiles,
    get_available_tags,
    resolve_scan_options,
    SCAN_PROFILES,
    NUCLEI_TEMPLATE_TAGS,
)
from app.schemas.scan import ScanProfile, ScanOptions


def test_get_available_profiles():
    profiles = get_available_profiles()
    assert len(profiles) >= 4
    profile_ids = [p["id"] for p in profiles]
    assert "quick" in profile_ids
    assert "full" in profile_ids
    assert "network" in profile_ids
    assert "custom" in profile_ids


def test_get_available_tags():
    tags = get_available_tags()
    assert len(tags) >= 8
    tag_ids = [t["id"] for t in tags]
    assert "cve" in tag_ids
    assert "rce" in tag_ids
    assert "auth-bypass" in tag_ids
    assert "misconfig" in tag_ids


def test_resolve_quick_profile():
    opts = resolve_scan_options("quick")
    assert opts["profile"] == "quick"
    assert opts["port_range"] == "1-1000"
    assert opts["nmap_timing"] == "T4"
    assert "cve" in opts["nuclei_tags"]


def test_resolve_full_profile():
    opts = resolve_scan_options("full")
    assert opts["profile"] == "full"
    assert "80" in opts["port_range"]
    assert "443" in opts["port_range"]
    assert "rce" in opts["nuclei_tags"]
    assert "auth-bypass" in opts["nuclei_tags"]


def test_resolve_network_profile():
    opts = resolve_scan_options("network")
    assert opts["profile"] == "network"
    assert opts["port_range"] == "1-10000"
    assert "network" in opts["nuclei_tags"]


def test_resolve_custom_profile_with_overrides():
    custom = ScanOptions(
        profile=ScanProfile.CUSTOM,
        port_range="22,80,443,3306,5432",
        nmap_timing="T5",
        nuclei_tags=["cve", "sqli", "exposure"],
        rate_limit=150,
        concurrency=15,
        severity_filter=["critical", "high"]
    )
    opts = resolve_scan_options("custom", custom)
    assert opts["profile"] == "custom"
    assert opts["port_range"] == "22,80,443,3306,5432"
    assert opts["nmap_timing"] == "T5"
    assert opts["nuclei_tags"] == ["cve", "sqli", "exposure"]
    assert opts["rate_limit"] == 150
    assert opts["concurrency"] == 15
    assert opts["severity_filter"] == ["critical", "high"]


def test_resolve_unknown_profile_fallback():
    opts = resolve_scan_options("nonexistent_profile")
    assert opts["profile"] == "quick"
    assert opts["port_range"] == "1-1000"
