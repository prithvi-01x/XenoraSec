# tests/test_batch_scan.py

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_batch_scan_with_cidr(client, monkeypatch):
    # Allow private for this test to test CIDR expansion
    monkeypatch.setattr(settings, "ALLOW_PRIVATE_IP_SCANNING", True)

    # 192.168.1.0/30 expands to .1 and .2 (2 usable hosts)
    payload = {
        "targets": ["192.168.1.0/30"],
        "scan_profile": "quick",
        "batch_name": "Test Subnet Batch",
        "options": {
            "allow_private": True
        }
    }

    res = client.post("/api/scan/batch", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "batch_id" in data
    assert data["batch_name"] == "Test Subnet Batch"
    assert data["total_targets"] == 2
    assert len(data["created_scans"]) == 2
    batch_id = data["batch_id"]

    # Verify status endpoint
    status_res = client.get(f"/api/scan/batch/{batch_id}")
    assert status_res.status_code == 200
    status_data = status_res.json()
    assert status_data["batch_id"] == batch_id
    assert status_data["total"] == 2
    assert len(status_data["scans"]) == 2
    targets = [s["target"] for s in status_data["scans"]]
    assert "192.168.1.1" in targets
    assert "192.168.1.2" in targets


def test_batch_scan_with_raw_multiline(client, monkeypatch):
    monkeypatch.setattr(settings, "ALLOW_PRIVATE_IP_SCANNING", True)

    raw_text = "192.168.1.10\n192.168.1.11, 192.168.1.12"
    payload = {
        "raw_targets": raw_text,
        "scan_profile": "quick",
        "options": {
            "allow_private": True
        }
    }

    res = client.post("/api/scan/batch", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["total_targets"] == 3
    assert len(data["created_scans"]) == 3


def test_batch_scan_validation_errors(client):
    # Empty targets
    res = client.post("/api/scan/batch", json={"targets": []})
    assert res.status_code == 400

    # Non-existent batch
    res_404 = client.get("/api/scan/batch/non-existent-uuid")
    assert res_404.status_code == 404


def test_single_scan_rejects_cidr_input(client, monkeypatch):
    monkeypatch.setattr(settings, "ALLOW_PRIVATE_IP_SCANNING", True)
    res = client.post("/api/scan/", json={"target": "192.168.1.0/28", "options": {"allow_private": True}})
    assert res.status_code == 400
    assert "batch" in res.json()["detail"].lower()
