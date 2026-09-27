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
