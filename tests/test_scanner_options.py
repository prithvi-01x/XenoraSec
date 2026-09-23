# tests/test_scanner_options.py

import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.services.scanner_service import run_full_scan
from app.schemas.scan import ScanOptions, ScanProfile


@pytest.mark.asyncio
async def test_run_full_scan_with_custom_profile():
    mock_nmap = AsyncMock(return_value={
        "status": "completed",
        "target": "example.com",
        "ports": [{"port": 80, "protocol": "tcp", "service": "http"}],
        "total_ports": 1
    })
    mock_nuclei = AsyncMock(return_value={
        "status": "completed",
        "target": "https://example.com",
        "vulnerabilities": [],
        "total_vulnerabilities": 0,
        "severity_distribution": {}
    })
    mock_ai = AsyncMock(return_value={
        "risk_score": 1.5,
        "summary": {
            "total_vulnerabilities": 0,
            "open_ports": 1,
            "severity_distribution": {},
            "critical_count": 0,
            "high_count": 0
        }
    })

    with patch("app.services.scanner_service.run_nmap_scan", mock_nmap), \
         patch("app.services.scanner_service.run_nuclei_scan", mock_nuclei), \
         patch("app.services.scanner_service.analyze_vulnerability_report", mock_ai):
        
        options = ScanOptions(
            profile=ScanProfile.CUSTOM,
            port_range="80,443",
            nmap_timing="T5",
            nuclei_tags=["rce", "cve"]
        )

        result = await run_full_scan(
            target="example.com",
            metadata={"type": "domain", "clean_target": "example.com"},
            parallel=True,
            scan_profile="custom",
            options=options
        )

        assert result["status"] == "completed"
        assert result["scan_profile"] == "custom"
        assert result["scan_options"]["port_range"] == "80,443"
        assert result["scan_options"]["nuclei_tags"] == ["rce", "cve"]

        # Verify nmap was called with custom port_range and timing
        mock_nmap.assert_called_once()
        _, nmap_kwargs = mock_nmap.call_args
        assert nmap_kwargs.get("port_range") == "80,443"
        assert nmap_kwargs.get("timing") == "T5"

        # Verify nuclei was called with custom tags
        mock_nuclei.assert_called_once()
        _, nuclei_kwargs = mock_nuclei.call_args
        assert nuclei_kwargs.get("tags") == ["rce", "cve"]


def test_api_profiles_and_templates_endpoints():
    client = TestClient(app)

    # Test GET /api/scan/profiles
    res = client.get("/api/scan/profiles")
    assert res.status_code == 200
    data = res.json()
    assert "profiles" in data
    profiles = [p["id"] for p in data["profiles"]]
    assert "quick" in profiles
    assert "full" in profiles
    assert "network" in profiles
    assert "custom" in profiles

    # Test GET /api/scan/templates
    res = client.get("/api/scan/templates")
    assert res.status_code == 200
    data = res.json()
    assert "tags" in data
    tag_ids = [t["id"] for t in data["tags"]]
    assert "cve" in tag_ids
    assert "rce" in tag_ids
