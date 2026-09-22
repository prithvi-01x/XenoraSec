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
