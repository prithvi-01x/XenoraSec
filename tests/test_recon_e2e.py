# tests/test_recon_e2e.py

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import AsyncSessionLocal
from app.db.crud import delete_asset
from app.schemas.recon import (
    SubdomainRecord,
    DNSIntelligence,
    DNSRecord,
    MailSecurityPosture,
    TechFingerprint,
    TechStackItem,
    SecurityHeaderCheck,
    ReconResult,
)
from datetime import datetime, UTC


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.mark.asyncio
async def test_full_passive_recon_and_asset_lifecycle(client, monkeypatch):
    """
    End-to-end workflow verification:
    1. Execute passive recon POST /api/recon
    2. Confirm response and auto-persistence to recon_history
    3. Retrieve cached result via GET /api/recon/{domain}
    4. Verify history listing via GET /api/recon/history
    5. Import subdomains into Asset Inventory
    6. Verify newly created assets in inventory
    7. Clean up created assets
    """
    domain = "e2e-target-domain.org"

    mock_result = ReconResult(
        domain=domain,
        target=domain,
        status="completed",
        timestamp=datetime.now(UTC),
        duration=1.85,
        subdomains_count=3,
        active_subdomains_count=2,
        subdomains=[
            SubdomainRecord(subdomain=f"api.{domain}", domain=domain, ip_addresses=["203.0.113.10"], is_active=True),
            SubdomainRecord(subdomain=f"auth.{domain}", domain=domain, ip_addresses=["203.0.113.11"], is_active=True),
            SubdomainRecord(subdomain=f"staging.{domain}", domain=domain, ip_addresses=[], is_active=False),
        ],
        dns=DNSIntelligence(
            domain=domain,
            records=[
                DNSRecord(record_type="A", host=domain, value="203.0.113.10"),
                DNSRecord(record_type="MX", host=domain, value="mail.e2e-target-domain.org", priority=10),
            ],
            nameservers=["ns1.e2e-target-domain.org"],
            mail_servers=["mail.e2e-target-domain.org"],
            ipv4_addresses=["203.0.113.10"],
            mail_security=MailSecurityPosture(
                has_spf=True,
                spf_record="v=spf1 -all",
                spf_status="pass",
                has_dmarc=True,
                dmarc_record="v=DMARC1; p=reject",
                dmarc_policy="reject",
                security_rating="secure",
            ),
        ),
        tech_stack=TechFingerprint(
            target_url=f"https://{domain}",
            status_code=200,
            title="E2E Corporate Portal",
            web_servers=[TechStackItem(name="Nginx", category="web_server", version="1.25.0")],
            frameworks=[TechStackItem(name="Next.js", category="framework")],
            all_technologies=[
                TechStackItem(name="Nginx", category="web_server", version="1.25.0"),
                TechStackItem(name="Next.js", category="framework"),
            ],
            security_headers=[
                SecurityHeaderCheck(header="Strict-Transport-Security", present=True, status="pass"),
                SecurityHeaderCheck(header="Content-Security-Policy", present=True, status="pass"),
            ],
            security_score=95,
        ),
    )

    from app.services.recon_service import recon_engine
    async def mock_execute(domain, **kwargs):
        # Also persist to db if db is passed
        db = kwargs.get("db")
        if db:
            from app.db.crud import save_recon_result
            await save_recon_result(
                db=db,
                domain=domain,
                result_dict=mock_result.model_dump(mode="json"),
                duration=mock_result.duration,
                subdomains_count=mock_result.subdomains_count,
                active_subdomains_count=mock_result.active_subdomains_count,
                tech_detected_count=2,
                security_score=95,
            )
        return mock_result

    monkeypatch.setattr(recon_engine, "execute_recon", mock_execute)

    # 1. POST /api/recon
    recon_res = client.post(
        "/api/recon",
        json={"domain": domain}
    )
    assert recon_res.status_code == 200
    recon_data = recon_res.json()
    assert recon_data["domain"] == domain
    assert recon_data["subdomains_count"] == 3
    assert recon_data["dns"]["mail_security"]["security_rating"] == "secure"
    assert recon_data["tech_stack"]["security_score"] == 95

    # 2. GET /api/recon/{domain}
    cached_res = client.get(f"/api/recon/{domain}")
    assert cached_res.status_code == 200
    assert cached_res.json()["domain"] == domain

    # 3. GET /api/recon/history
    hist_res = client.get(f"/api/recon/history?domain={domain}")
    assert hist_res.status_code == 200
    assert hist_res.json()["total"] >= 1

    # 4. POST /api/recon/{domain}/import-to-assets
    import_res = client.post(
        f"/api/recon/{domain}/import-to-assets",
        json={
            "subdomains": [f"api.{domain}", f"auth.{domain}"],
            "target_status": "active",
            "default_criticality": "high",
        }
    )
    assert import_res.status_code == 200
    import_data = import_res.json()
    assert import_data["imported_count"] == 2
    asset_ids = import_data["asset_ids"]

    try:
        # 5. Verify assets in Asset Inventory
        assets_res = client.get(f"/api/assets?search={domain}")
        assert assets_res.status_code == 200
        items = assets_res.json()["items"]
        assert len(items) >= 2
        hostnames = [item["hostname"] for item in items]
        assert f"api.{domain}" in hostnames
        assert f"auth.{domain}" in hostnames

    finally:
        async with AsyncSessionLocal() as session:
            for aid in asset_ids:
                await delete_asset(session, aid)
