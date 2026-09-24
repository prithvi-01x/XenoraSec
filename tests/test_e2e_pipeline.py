"""
End-to-end integration test validating the entire pipeline:
1. Batch scan creation and target parsing
2. Batch status aggregation
3. Asset inventory automated ingestion from scan results
4. Asset delta update / upsert lifecycle
5. Asset search, filtering, and stats aggregation
6. Asset deletion cleanup
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.db.database import AsyncSessionLocal
from app.db.crud import upsert_asset_from_scan, delete_asset


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.mark.asyncio
async def test_full_batch_to_asset_pipeline_lifecycle(client, monkeypatch):
    monkeypatch.setattr(settings, "ALLOW_PRIVATE_IP_SCANNING", True)

    target1 = "10.10.10.1"
    target2 = "10.10.10.2"

    # Step 1: Create batch scan via REST API
    batch_req = {
        "raw_targets": f"{target1}, {target2}",
        "batch_name": "E2E Pipeline Integration Test",
        "scan_profile": "quick",
        "options": {
            "allow_private": True
        }
    }
    batch_resp = client.post("/api/scan/batch", json=batch_req)
    assert batch_resp.status_code == 200
    batch_data = batch_resp.json()
    batch_id = batch_data["batch_id"]
    assert batch_data["total_targets"] == 2
    assert len(batch_data["created_scans"]) == 2

    # Step 2: Check batch status endpoint
    status_resp = client.get(f"/api/scan/batch/{batch_id}")
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["batch_id"] == batch_id
    assert status_data["total"] == 2

    # Step 3: Simulate scanner completion and automated Asset ingestion
    scan_result_1 = {
        "nmap": {
            "ports": [
                {"port": 80, "protocol": "tcp", "service": "http", "product": "nginx", "version": "1.24"},
                {"port": 443, "protocol": "tcp", "service": "https", "product": "nginx", "version": "1.24"},
            ]
        },
        "nuclei": {
            "vulnerabilities": [
                {
                    "template_id": "cve-2023-44487",
                    "name": "HTTP/2 Rapid Reset Attack",
                    "severity": "high",
                    "cve": "CVE-2023-44487",
                    "cvss": 7.5,
                    "matched_at": f"https://{target1}",
                }
            ]
        }
    }

    scan_result_2 = {
        "nmap": {
            "ports": [
                {"port": 22, "protocol": "tcp", "service": "ssh", "product": "OpenSSH", "version": "9.0"},
            ]
        },
        "nuclei": {
            "vulnerabilities": []
        }
    }

    asset_ids = []
    async with AsyncSessionLocal() as session:
        a1 = await upsert_asset_from_scan(
            db=session,
            target=target1,
            scan_result=scan_result_1,
            risk_score=7.5
        )
        assert a1 is not None
        asset_ids.append(a1.id)

        a2 = await upsert_asset_from_scan(
            db=session,
            target=target2,
            scan_result=scan_result_2,
            risk_score=0.0
        )
        assert a2 is not None
        asset_ids.append(a2.id)

    try:
        # Step 4: Verify Assets via REST API
        list_resp = client.get("/api/assets?search=10.10.10.")
        assert list_resp.status_code == 200
        items = list_resp.json()["items"]
        assert len(items) == 2

        # Step 5: Verify Asset 1 details (ports and vulnerabilities)
        a1_resp = client.get(f"/api/assets/{asset_ids[0]}")
        assert a1_resp.status_code == 200
        a1_data = a1_resp.json()
        assert a1_data["open_ports_count"] == 2
        assert a1_data["vulnerabilities_count"] == 1
        assert a1_data["risk_score"] == 7.5
        assert len(a1_data["ports"]) == 2
        assert len(a1_data["vulnerabilities"]) == 1
        assert a1_data["vulnerabilities"][0]["template_id"] == "cve-2023-44487"

        # Step 6: Test Delta / Upsert lifecycle on Asset 1 (new port discovered)
        scan_result_1_updated = {
            "nmap": {
                "ports": [
                    {"port": 80, "protocol": "tcp", "service": "http", "product": "nginx", "version": "1.25"},
                    {"port": 443, "protocol": "tcp", "service": "https", "product": "nginx", "version": "1.25"},
                    {"port": 8080, "protocol": "tcp", "service": "http-proxy", "product": "envoy", "version": "1.28"},
                ]
            },
            "nuclei": {
                "vulnerabilities": scan_result_1["nuclei"]["vulnerabilities"]
            }
        }

        async with AsyncSessionLocal() as session:
            updated_a1 = await upsert_asset_from_scan(
                db=session,
                target=target1,
                scan_result=scan_result_1_updated,
                risk_score=7.8
            )
            assert updated_a1.id == asset_ids[0]

        a1_refetched = client.get(f"/api/assets/{asset_ids[0]}").json()
        assert a1_refetched["open_ports_count"] == 3
        assert a1_refetched["risk_score"] == 7.8

        # Step 7: Update asset metadata (criticality & notes)
        patch_resp = client.patch(
            f"/api/assets/{asset_ids[0]}",
            json={"criticality": "critical", "notes": "Production gateway identified in audit"}
        )
        assert patch_resp.status_code == 200
        assert patch_resp.json()["criticality"] == "critical"
        assert patch_resp.json()["notes"] == "Production gateway identified in audit"

        # Step 8: Asset Stats API verification
        stats_resp = client.get("/api/assets/stats")
        assert stats_resp.status_code == 200
        stats = stats_resp.json()
        assert stats["total_assets"] >= 2
        assert stats["total_open_ports"] >= 3
        assert stats["total_vulnerabilities"] >= 1

    finally:
        # Step 9: Cleanup
        async with AsyncSessionLocal() as session:
            for aid in asset_ids:
                await delete_asset(session, aid)
