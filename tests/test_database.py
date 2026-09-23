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

