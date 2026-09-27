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


@pytest.mark.asyncio
async def test_get_domain_recon_and_history(client):
    from app.db.database import AsyncSessionLocal
    from app.db.crud import save_recon_result

    target = "history-recon-test.io"
    sample_payload = {
        "domain": target,
        "target": target,
        "status": "completed",
        "timestamp": datetime.now(UTC).isoformat(),
        "duration": 2.5,
        "subdomains_count": 1,
        "active_subdomains_count": 1,
        "subdomains": [
            {"subdomain": f"app.{target}", "domain": target, "ip_addresses": ["1.1.1.1"], "is_active": True}
        ],
        "dns": {
            "domain": target,
            "records": [{"record_type": "A", "host": target, "value": "1.1.1.1"}],
            "nameservers": ["ns1.cloudflare.com"],
            "ipv4_addresses": ["1.1.1.1"],
        },
        "tech_stack": {
            "target_url": f"https://{target}",
            "status_code": 200,
            "title": "History Portal",
            "web_servers": [{"name": "Cloudflare", "category": "cdn_waf"}],
            "all_technologies": [{"name": "Cloudflare", "category": "cdn_waf"}],
            "security_headers": [],
            "security_score": 90,
        }
    }

    # 1. Seed database with recon history record
    async with AsyncSessionLocal() as session:
        await save_recon_result(
            db=session,
            domain=target,
            result_dict=sample_payload,
            duration=2.5,
            subdomains_count=1,
            active_subdomains_count=1,
            tech_detected_count=1,
            security_score=90,
            status="completed"
        )

    # 2. Test GET /api/recon/{domain}
    res = client.get(f"/api/recon/{target}")
    assert res.status_code == 200
    res_data = res.json()
    assert res_data["domain"] == target
    assert res_data["subdomains_count"] == 1
    assert res_data["tech_stack"]["security_score"] == 90

    # 3. Test GET non-existent domain -> 404
    missing_res = client.get("/api/recon/unknown-never-scanned.xyz")
    assert missing_res.status_code == 404

    # 4. Test GET /api/recon/history
    hist_res = client.get("/api/recon/history?limit=10")
    assert hist_res.status_code == 200
    hist_data = hist_res.json()
    assert "items" in hist_data
    assert "total" in hist_data
    assert hist_data["total"] >= 1
    assert any(item["domain"] == target for item in hist_data["items"])

    # 5. Filter history by domain
    filtered_res = client.get(f"/api/recon/history?domain={target[:10]}")
    assert filtered_res.status_code == 200
    assert filtered_res.json()["total"] >= 1


@pytest.mark.asyncio
async def test_import_to_assets_endpoint(client):
    from app.db.database import AsyncSessionLocal
    from app.db.crud import save_recon_result, delete_asset

    target = "asset-sync-corp.com"
    sample_subdomains = [
        {"subdomain": f"vpn.{target}", "domain": target, "ip_addresses": ["198.51.100.1"], "is_active": True},
        {"subdomain": f"mail.{target}", "domain": target, "ip_addresses": ["198.51.100.2"], "is_active": True},
    ]

    async with AsyncSessionLocal() as session:
        await save_recon_result(
            db=session,
            domain=target,
            result_dict={"domain": target, "subdomains": sample_subdomains},
            duration=1.0,
            subdomains_count=2,
            active_subdomains_count=2,
            tech_detected_count=0,
            security_score=50,
            status="completed"
        )

    # 1. Post import request
    import_res = client.post(
        f"/api/recon/{target}/import-to-assets",
        json={
            "subdomains": None,
            "target_status": "active",
            "default_criticality": "high",
            "tags": ["recon-test"]
        }
    )
    assert import_res.status_code == 200
    import_data = import_res.json()
    assert import_data["domain"] == target
    assert import_data["imported_count"] == 2
    assert import_data["skipped_count"] == 0
    assert len(import_data["asset_ids"]) == 2
    asset_ids = import_data["asset_ids"]

    try:
        # 2. Check that assets appear in GET /api/assets
        list_res = client.get(f"/api/assets?search={target}")
        assert list_res.status_code == 200
        found_hosts = [a["hostname"] for a in list_res.json()["items"]]
        assert f"vpn.{target}" in found_hosts
        assert f"mail.{target}" in found_hosts

        # 3. Test re-importing (should skip existing)
        reimport_res = client.post(
            f"/api/recon/{target}/import-to-assets",
            json={"subdomains": None}
        )
        assert reimport_res.status_code == 200
        reimport_data = reimport_res.json()
        assert reimport_data["imported_count"] == 0
        assert reimport_data["skipped_count"] == 2

        # 4. Test 404 on un-scanned domain
        missing_res = client.post("/api/recon/non-existent-recon-site.net/import-to-assets", json={})
        assert missing_res.status_code == 404

    finally:
        async with AsyncSessionLocal() as session:
            for aid in asset_ids:
                await delete_asset(session, aid)


