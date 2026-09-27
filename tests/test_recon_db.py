# tests/test_recon_db.py

import pytest
from app.db.database import AsyncSessionLocal
from app.db.crud import (
    save_recon_result,
    get_latest_recon_by_domain,
    get_recon_history,
)


@pytest.mark.asyncio
async def test_recon_history_save_and_retrieve():
    """Verify storing and retrieving passive recon assessment history."""
    async with AsyncSessionLocal() as session:
        domain = "osint-test-example.org"
        sample_result = {
            "domain": domain,
            "subdomains": [
                {"subdomain": f"api.{domain}", "ip_addresses": ["93.184.216.34"], "is_active": True},
                {"subdomain": f"mail.{domain}", "ip_addresses": ["93.184.216.35"], "is_active": True},
            ],
            "dns": {
                "domain": domain,
                "records": [
                    {"record_type": "A", "host": domain, "value": "93.184.216.34"}
                ]
            },
            "tech_stack": {
                "target_url": f"https://{domain}",
                "web_servers": [{"name": "nginx", "category": "web_server"}],
                "security_score": 85
            }
        }

        # 1. Save recon record
        saved = await save_recon_result(
            db=session,
            domain=domain,
            result_dict=sample_result,
            duration=3.45,
            subdomains_count=2,
            active_subdomains_count=2,
            tech_detected_count=1,
            security_score=85,
            status="completed"
        )
        assert saved is not None
        assert saved.id is not None
        assert saved.domain == domain
        assert saved.subdomains_count == 2
        assert saved.security_score == 85
        assert saved.result["tech_stack"]["security_score"] == 85

        # 2. Query latest recon
        latest = await get_latest_recon_by_domain(session, domain)
        assert latest is not None
        assert latest.id == saved.id
        assert latest.domain == domain

        # 3. Query paginated recon history
        history, total = await get_recon_history(session, limit=10, domain="osint-test")
        assert total >= 1
        assert any(item.domain == domain for item in history)


@pytest.mark.asyncio
async def test_import_recon_subdomains_to_asset_inventory():
    """Verify importing discovered subdomains into the Asset Inventory database."""
    from app.db.crud import import_recon_subdomains_to_assets, get_asset_by_id
    from app.db.models import Asset
    from sqlalchemy import select

    async with AsyncSessionLocal() as session:
        domain = "import-osint.corp"
        subdomain_records = [
            {
                "subdomain": f"auth.{domain}",
                "ip_addresses": ["104.21.50.1"],
                "source": "crtsh",
                "is_active": True
            },
            {
                "subdomain": f"vpn.{domain}",
                "ip_addresses": ["104.21.50.2"],
                "source": "crtsh",
                "is_active": True
            },
            {
                "subdomain": f"dev.{domain}",
                "ip_addresses": ["104.21.50.3"],
                "source": "passive_dns",
                "is_active": False
            },
        ]

        # 1. Bulk import all subdomains
        imported, skipped, asset_ids = await import_recon_subdomains_to_assets(
            db=session,
            domain=domain,
            subdomain_records=subdomain_records,
            selected_subdomains=None,
            target_status="active",
            default_criticality="high",
            tags=["recon-tag1"]
        )

        assert imported == 3
        assert skipped == 0
        assert len(asset_ids) == 3

        # Verify created asset attributes
        stmt = select(Asset).where(Asset.hostname == f"auth.{domain}")
        res = await session.execute(stmt)
        auth_asset = res.scalar_one_or_none()
        assert auth_asset is not None
        assert auth_asset.ip_address == "104.21.50.1"
        assert auth_asset.asset_type == "domain"
        assert auth_asset.criticality == "high"
        assert "recon-discovered" in auth_asset.tags
        assert "recon-tag1" in auth_asset.tags

        # 2. Re-importing should skip existing and merge tags
        imported_again, skipped_again, asset_ids_again = await import_recon_subdomains_to_assets(
            db=session,
            domain=domain,
            subdomain_records=subdomain_records,
            selected_subdomains=[f"auth.{domain}"],
            tags=["recon-tag2"]
        )
        assert imported_again == 0
        assert skipped_again == 1
        assert auth_asset.id in asset_ids_again

        # Check tag merge
        res = await session.execute(stmt)
        auth_asset_updated = res.scalar_one_or_none()
        assert "recon-tag2" in auth_asset_updated.tags

