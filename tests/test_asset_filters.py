# tests/test_asset_filters.py

import pytest
from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.db.models import Asset, AssetPort, AssetVulnerability
from app.db.crud import (
    upsert_asset_from_scan,
    get_assets,
    get_asset_by_id,
    delete_asset,
    update_asset
)


@pytest.mark.asyncio
async def test_asset_inventory_type_and_criticality_filters():
    async with AsyncSessionLocal() as session:
        # Seed 3 distinct assets
        a1 = await upsert_asset_from_scan(
            session,
            target="10.10.10.1",
            scan_result={"nmap": {"ports": []}, "nuclei": {"vulnerabilities": []}},
            risk_score=1.5
        )
        a2 = await upsert_asset_from_scan(
            session,
            target="web-portal.local",
            scan_result={
                "nmap": {"ports": [{"port": 443, "service": "https"}]},
                "nuclei": {
                    "vulnerabilities": [
                        {"name": "SQL Injection", "severity": "high", "template_id": "sqli-1"}
                    ]
                }
            },
            risk_score=8.5
        )
        a3 = await upsert_asset_from_scan(
            session,
            target="http://api-service.local:8080/v1",
            scan_result={
                "nmap": {"ports": [{"port": 8080, "service": "http-alt"}]},
                "nuclei": {
                    "vulnerabilities": [
                        {"name": "Critical Auth Bypass", "severity": "critical", "template_id": "auth-1"}
                    ]
                }
            },
            risk_score=9.9
        )

        assert a1 is not None and a2 is not None and a3 is not None
        id1, id2, id3 = a1.id, a2.id, a3.id

    try:
        async with AsyncSessionLocal() as session:
            # 1. Filter by asset_type
            ip_assets, _ = await get_assets(session, asset_type="ip")
            assert any(a.id == id1 for a in ip_assets)

            url_assets, _ = await get_assets(session, asset_type="url")
            assert any(a.id == id3 for a in url_assets)

            # 2. Filter by criticality
            crit_assets, _ = await get_assets(session, criticality="critical")
            assert any(a.id == id3 for a in crit_assets)

            high_assets, _ = await get_assets(session, criticality="high")
            assert any(a.id == id2 for a in high_assets)

            # 3. Filter by min_risk
            high_risk, _ = await get_assets(session, min_risk=8.0)
            assert any(a.id == id2 for a in high_risk)
            assert any(a.id == id3 for a in high_risk)
            assert not any(a.id == id1 for a in high_risk)

            # 4. Update status and filter by status
            await update_asset(session, asset_id=id1, status="inactive")
            inactive_assets, _ = await get_assets(session, status="inactive")
            assert any(a.id == id1 for a in inactive_assets)

    finally:
        async with AsyncSessionLocal() as session:
            for aid in (id1, id2, id3):
                await delete_asset(session, aid)


@pytest.mark.asyncio
async def test_asset_cascade_deletion():
    async with AsyncSessionLocal() as session:
        asset = await upsert_asset_from_scan(
            session,
            target="cascade-test.local",
            scan_result={
                "nmap": {"ports": [{"port": 80, "service": "http"}]},
                "nuclei": {"vulnerabilities": [{"name": "Exposure", "severity": "low", "template_id": "exp-1"}]}
            },
            risk_score=3.0
        )
        assert asset is not None
        aid = asset.id

        # Verify ports and vulns were inserted
        ports = (await session.execute(select(AssetPort).where(AssetPort.asset_id == aid))).scalars().all()
        vulns = (await session.execute(select(AssetVulnerability).where(AssetVulnerability.asset_id == aid))).scalars().all()
        assert len(ports) == 1
        assert len(vulns) == 1

        # Delete asset
        deleted = await delete_asset(session, aid)
        assert deleted is True

        # Verify cascading deletion of children
        orphan_ports = (await session.execute(select(AssetPort).where(AssetPort.asset_id == aid))).scalars().all()
        orphan_vulns = (await session.execute(select(AssetVulnerability).where(AssetVulnerability.asset_id == aid))).scalars().all()
        assert len(orphan_ports) == 0
        assert len(orphan_vulns) == 0
