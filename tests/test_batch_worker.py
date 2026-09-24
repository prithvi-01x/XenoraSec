# tests/test_batch_worker.py

import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import AsyncSessionLocal
from app.db.crud import create_scan, update_scan_result, mark_scan_failed
from app.schemas.scan import ScanStatus


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.mark.asyncio
async def test_batch_status_aggregation_with_mixed_results(client):
    batch_id = str(uuid4())
    s1_id = str(uuid4())
    s2_id = str(uuid4())
    s3_id = str(uuid4())

    async with AsyncSessionLocal() as session:
        # Scan 1: Completed with risk score 8.0
        await create_scan(session, scan_id=s1_id, target="target1.local", batch_id=batch_id)
        await update_scan_result(
            session,
            scan_id=s1_id,
            result={"status": "completed"},
            risk_score=8.0,
            duration=12.5,
            status=ScanStatus.COMPLETED.value
        )

        # Scan 2: Failed with error
        await create_scan(session, scan_id=s2_id, target="target2.local", batch_id=batch_id)
        await mark_scan_failed(
            session,
            scan_id=s2_id,
            error="Connection timed out",
            status=ScanStatus.FAILED.value
        )

        # Scan 3: Running
        await create_scan(session, scan_id=s3_id, target="target3.local", batch_id=batch_id)

    # Fetch status via API endpoint
    res = client.get(f"/api/scan/batch/{batch_id}")
    assert res.status_code == 200
    data = res.json()

    assert data["batch_id"] == batch_id
    assert data["total"] == 3
    assert data["completed"] == 1
    assert data["failed"] == 1
    assert data["running"] == 1
    assert data["pending"] == 0
    assert data["overall_risk_score"] == 8.0

    targets = {s["scan_id"]: s for s in data["scans"]}
    assert targets[s1_id]["status"] == "completed"
    assert targets[s1_id]["risk_score"] == 8.0
    assert targets[s2_id]["status"] == "failed"
    assert targets[s2_id]["error"] == "Connection timed out"
    assert targets[s3_id]["status"] == "running"
