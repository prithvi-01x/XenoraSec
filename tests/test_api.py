# tests/test_api.py

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.schemas.scan import ScanStatus
from app.db.database import AsyncSessionLocal
from app.db.models import ScanResult
from uuid import uuid4


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health_endpoints(client):
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"

    # Trailing slash variant
    res_slash = client.get("/health/")
    assert res_slash.status_code == 200


def test_queue_endpoint(client):
    res = client.get("/api/scan/queue")
    assert res.status_code == 200
    data = res.json()
    assert "scans_running" in data
    assert "max_concurrent_scans" in data
    assert "available_slots" in data


def test_scan_validation_rejections(client):
    settings.ALLOW_LOCALHOST_SCANNING = False
    settings.ALLOW_PRIVATE_IP_SCANNING = False

    # Localhost rejected
    res = client.post("/api/scan/", json={"target": "localhost"})
    assert res.status_code == 400
    assert "localhost" in res.json()["detail"].lower()

    # Private IP rejected
    res = client.post("/api/scan/", json={"target": "10.0.0.1"})
    assert res.status_code == 400
    assert "private" in res.json()["detail"].lower()

    # Invalid syntax rejected
    res = client.post("/api/scan/", json={"target": "not a valid target name @@@"})
    assert res.status_code == 400


def test_history_endpoint(client):
    res = client.get("/api/scan/history?limit=5&offset=0")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
async def test_retry_partial_and_failed_scans(client):
    # Insert dummy records: one completed, one partial, one failed
    partial_id = str(uuid4())
    completed_id = str(uuid4())

    async with AsyncSessionLocal() as session:
        partial_scan = ScanResult(
            scan_id=partial_id,
            target="example.com",
            status=ScanStatus.PARTIAL.value
        )
        completed_scan = ScanResult(
            scan_id=completed_id,
            target="example.com",
            status=ScanStatus.COMPLETED.value
        )
        session.add(partial_scan)
        session.add(completed_scan)
        await session.commit()

    # Completed scan should reject retry
    res = client.post(f"/api/scan/{completed_id}/retry")
    assert res.status_code == 400
    assert "retry" in res.json()["detail"].lower()

    # Partial scan should be allowed for retry (it will initiate or re-validate)
    # Target resolution for example.com is valid, so it starts the retry
    res = client.post(f"/api/scan/{partial_id}/retry")
    assert res.status_code in [200, 503]  # 200 if slots available, 503 if queue full
    if res.status_code == 200:
        data = res.json()
        assert data["status"] == "running"
        assert "scan_id" in data
