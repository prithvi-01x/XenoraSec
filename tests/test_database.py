# tests/test_database.py

import pytest
import asyncio
from sqlalchemy import text
from app.db.database import engine, IS_SQLITE, AsyncSessionLocal


@pytest.mark.asyncio
async def test_database_pragmas_applied():
    if not IS_SQLITE:
        pytest.skip("Test specifically covers SQLite PRAGMAs")

    async with engine.connect() as conn:
        res = await conn.execute(text("PRAGMA busy_timeout"))
        timeout = res.scalar()
        assert timeout == 30000


@pytest.mark.asyncio
async def test_concurrent_sessions():
    async def query_worker(i):
        async with AsyncSessionLocal() as session:
            res = await session.execute(text("SELECT 1"))
            return res.scalar()

    # Launch 10 concurrent queries
    results = await asyncio.gather(*[query_worker(i) for i in range(10)])
    assert all(r == 1 for r in results)


@pytest.mark.asyncio
async def test_get_scan_statistics():
    from app.db.crud import create_scan, update_scan_result, get_scan_statistics
    from uuid import uuid4

    scan_id1 = str(uuid4())
    scan_id2 = str(uuid4())

    async with AsyncSessionLocal() as session:
        await create_scan(session, scan_id=scan_id1, target="stats-test1.com")
        await update_scan_result(session, scan_id=scan_id1, result={"status": "completed"}, risk_score=8.0)

        await create_scan(session, scan_id=scan_id2, target="stats-test2.com")
        await update_scan_result(session, scan_id=scan_id2, result={"status": "completed"}, risk_score=4.0)

        stats = await get_scan_statistics(session)

    assert stats["total_scans"] >= 2
    assert "status_counts" in stats
    assert stats["status_counts"]["completed"] >= 2
    assert isinstance(stats["average_risk_score"], float)
    assert stats["average_risk_score"] > 0.0


@pytest.mark.asyncio
async def test_cleanup_old_scans():
    from app.db.crud import cleanup_old_scans, get_scan
    from app.db.models import ScanResult
    from datetime import datetime, UTC, timedelta
    from uuid import uuid4

    old_scan_id = str(uuid4())
    recent_scan_id = str(uuid4())

    async with AsyncSessionLocal() as session:
        old_scan = ScanResult(
            scan_id=old_scan_id,
            target="old-target.com",
            status="completed",
            created_at=datetime.now(UTC) - timedelta(days=60),
            updated_at=datetime.now(UTC) - timedelta(days=60),
        )
        recent_scan = ScanResult(
            scan_id=recent_scan_id,
            target="recent-target.com",
            status="completed",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        session.add(old_scan)
        session.add(recent_scan)
        await session.commit()

    async with AsyncSessionLocal() as session:
        deleted_count = await cleanup_old_scans(session, days=30)
        assert deleted_count >= 1

        # Old scan should be deleted
        assert await get_scan(session, old_scan_id) is None
        # Recent scan should still exist
        assert await get_scan(session, recent_scan_id) is not None


@pytest.mark.asyncio
async def test_asset_inventory_crud_operations():
    from app.db.crud import (
        upsert_asset_from_scan,
        get_assets,
        get_asset_by_id,
        update_asset,
        delete_asset,
        get_asset_statistics,
        create_scan,
        get_scans_by_batch,
    )
    from uuid import uuid4

    batch_id = str(uuid4())

    async with AsyncSessionLocal() as session:
        # 1. Test batch scan association
        scan1 = await create_scan(session, scan_id=str(uuid4()), target="192.168.1.10", batch_id=batch_id)
        scan2 = await create_scan(session, scan_id=str(uuid4()), target="192.168.1.11", batch_id=batch_id)
        assert scan1 is not None and scan2 is not None

        batch_scans = await get_scans_by_batch(session, batch_id)
        assert len(batch_scans) == 2

        # 2. Test upsert_asset_from_scan
        sample_scan_result = {
            "nmap": {
                "ports": [
                    {"port": 80, "protocol": "tcp", "service": "http", "product": "nginx", "version": "1.24"},
                    {"port": 443, "protocol": "tcp", "service": "https", "product": "nginx", "version": "1.24"},
                ]
            },
            "nuclei": {
                "vulnerabilities": [
                    {
                        "template_id": "cve-2023-1234",
                        "name": "Nginx Remote Buffer Overflow",
                        "severity": "critical",
                        "cve": "CVE-2023-1234",
                        "cvss": 9.8,
                        "matched_at": "https://test-asset.example.com",
                    },
                    {
                        "template_id": "tls-weak-cipher",
                        "name": "Weak TLS Cipher Suite",
                        "severity": "medium",
                        "cvss": 4.5,
                        "matched_at": "https://test-asset.example.com",
                    }
                ]
            }
        }

        asset = await upsert_asset_from_scan(
            session,
            target="test-asset.example.com",
            scan_result=sample_scan_result,
            risk_score=9.5
        )
        assert asset is not None
        assert asset.hostname == "test-asset.example.com"
        assert asset.open_ports_count == 2
        assert asset.vulnerabilities_count == 2
        assert asset.critical_count == 1
        assert asset.medium_count == 1
        assert asset.criticality == "critical"
        assert asset.risk_score == 9.5
        asset_id = asset.id

        # 3. Test get_asset_by_id with relationships loaded
        fetched_asset = await get_asset_by_id(session, asset_id)
        assert fetched_asset is not None
        assert len(fetched_asset.ports) == 2
        assert len(fetched_asset.vulnerabilities) == 2

        # 4. Test get_assets search and filtering
        assets_list, total = await get_assets(session, search="test-asset")
        assert total >= 1
        assert any(a.id == asset_id for a in assets_list)

        # Filter by min_risk
        high_risk_assets, _ = await get_assets(session, min_risk=9.0)
        assert any(a.id == asset_id for a in high_risk_assets)

        # 5. Test update_asset
        updated = await update_asset(
            session,
            asset_id=asset_id,
            status="inactive",
            notes="Primary edge load balancer",
            tags=["production", "dmz"]
        )
        assert updated is not None
        assert updated.status == "inactive"
        assert updated.notes == "Primary edge load balancer"
        assert "production" in updated.tags

        # 6. Test get_asset_statistics
        stats = await get_asset_statistics(session)
        assert stats["total_assets"] >= 1
        assert stats["total_open_ports"] >= 2
        assert stats["total_vulnerabilities"] >= 2

        # 7. Test delete_asset
        deleted = await delete_asset(session, asset_id)
        assert deleted is True
        assert await get_asset_by_id(session, asset_id) is None


