# tests/test_asset_routes.py

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import AsyncSessionLocal
from app.db.crud import upsert_asset_from_scan, delete_asset


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.mark.asyncio
async def test_asset_routes_end_to_end(client):
    # 1. Seed an asset via scan ingestion
    sample_scan = {
        "nmap": {
            "ports": [
                {"port": 80, "protocol": "tcp", "service": "http", "product": "Apache", "version": "2.4.52"},
                {"port": 22, "protocol": "tcp", "service": "ssh", "product": "OpenSSH", "version": "8.9"},
            ]
        },
        "nuclei": {
            "vulnerabilities": [
                {
                    "template_id": "cve-2024-9999",
                    "name": "Apache Remote Code Execution",
                    "severity": "critical",
                    "cve": "CVE-2024-9999",
                    "cvss": 9.8,
                    "matched_at": "http://api-asset-test.local",
                }
            ]
        }
    }

    async with AsyncSessionLocal() as session:
        created_asset = await upsert_asset_from_scan(
            db=session,
            target="api-asset-test.local",
            scan_result=sample_scan,
            risk_score=9.8
        )
        assert created_asset is not None
        asset_id = created_asset.id

    try:
        # 2. Test GET /api/assets
        res = client.get("/api/assets")
        assert res.status_code == 200
        data = res.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1
        assert any(item["id"] == asset_id for item in data["items"])

        # Filter by search
        search_res = client.get("/api/assets?search=api-asset-test")
        assert search_res.status_code == 200
        assert search_res.json()["total"] >= 1

        # 3. Test GET /api/assets/stats
        stats_res = client.get("/api/assets/stats")
        assert stats_res.status_code == 200
        stats = stats_res.json()
        assert stats["total_assets"] >= 1
        assert stats["total_open_ports"] >= 2
        assert stats["total_vulnerabilities"] >= 1

        # 4. Test GET /api/assets/{id}
        detail_res = client.get(f"/api/assets/{asset_id}")
        assert detail_res.status_code == 200
        detail = detail_res.json()
        assert detail["id"] == asset_id
        assert len(detail["ports"]) == 2
        assert len(detail["vulnerabilities"]) == 1
        assert detail["criticality"] == "critical"

        # 5. Test PATCH /api/assets/{id}
        patch_res = client.patch(
            f"/api/assets/{asset_id}",
            json={
                "criticality": "high",
                "status": "active",
                "notes": "Internal gateway asset",
                "tags": ["cloud", "production"]
            }
        )
        assert patch_res.status_code == 200
        patched = patch_res.json()
        assert patched["criticality"] == "high"
        assert patched["notes"] == "Internal gateway asset"
        assert "cloud" in patched["tags"]

        # 6. Test GET non-existent asset 404
        missing_res = client.get("/api/assets/99999999")
        assert missing_res.status_code == 404

        # 7. Test DELETE /api/assets/{id}
        del_res = client.delete(f"/api/assets/{asset_id}")
        assert del_res.status_code == 200
        assert del_res.json()["asset_id"] == asset_id

        # Verify deletion
        assert client.get(f"/api/assets/{asset_id}").status_code == 404

    finally:
        # Cleanup safety
        async with AsyncSessionLocal() as session:
            await delete_asset(session, asset_id)
