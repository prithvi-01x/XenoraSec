# tests/test_recon_routes.py

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.recon import (
    SubdomainRecord,
    DNSIntelligence,
    DNSRecord,
    TechFingerprint,
    TechStackItem,
    ReconResult,
)
from datetime import datetime, UTC


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_post_recon_validation_errors(client):
    # 1. Invalid domain characters
    res = client.post("/api/recon", json={"domain": "invalid;domain!name"})
    assert res.status_code == 400
    assert "Invalid target domain" in res.json()["detail"]

    # 2. Empty domain
    res = client.post("/api/recon", json={"domain": ""})
    assert res.status_code == 422  # Pydantic min_length error


def test_post_recon_successful_execution(client, monkeypatch):
    target = "api-recon-test.com"

    mock_result = ReconResult(
        domain=target,
        target=f"https://{target}",
        status="completed",
        timestamp=datetime.now(UTC),
        duration=1.25,
        subdomains_count=2,
        active_subdomains_count=2,
        subdomains=[
            SubdomainRecord(subdomain=f"auth.{target}", domain=target, ip_addresses=["10.0.0.1"], is_active=True),
            SubdomainRecord(subdomain=f"api.{target}", domain=target, ip_addresses=["10.0.0.2"], is_active=True),
        ],
        dns=DNSIntelligence(
            domain=target,
            records=[DNSRecord(record_type="A", host=target, value="10.0.0.1")],
            ipv4_addresses=["10.0.0.1"],
        ),
        tech_stack=TechFingerprint(
            target_url=f"https://{target}",
            status_code=200,
            title="API Test Portal",
            web_servers=[TechStackItem(name="Nginx", category="web_server", version="1.24.0")],
            all_technologies=[TechStackItem(name="Nginx", category="web_server", version="1.24.0")],
            security_score=85,
        ),
    )

    from app.services.recon_service import recon_engine
    async def mock_execute(**kwargs):
        return mock_result
    monkeypatch.setattr(recon_engine, "execute_recon", mock_execute)


    res = client.post(
        "/api/recon",
        json={
            "domain": f"https://{target}:8443/login",
            "include_subdomains": True,
            "resolve_subdomains": True,
            "include_dns": True,
            "include_tech_stack": True,
        }
    )

    assert res.status_code == 200
    data = res.json()
    assert data["domain"] == target
    assert data["subdomains_count"] == 2
    assert data["active_subdomains_count"] == 2
    assert len(data["subdomains"]) == 2
    assert data["tech_stack"]["security_score"] == 85
    assert data["tech_stack"]["web_servers"][0]["name"] == "Nginx"
