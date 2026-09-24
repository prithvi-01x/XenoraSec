"""
Tests for Asset and Batch schema validation and serialization.
"""
from datetime import datetime, timezone
import pytest
from pydantic import ValidationError

from app.schemas.scan import (
    BatchScanCreateRequest,
    BatchScanItem,
    BatchScanCreateResponse,
    BatchScanStatusResponse,
    ScanStatus,
    ScanProfile,
)
from app.schemas.asset import (
    AssetUpdateRequest,
    AssetResponse,
    AssetDetailResponse,
    AssetListResponse,
    AssetStatsResponse,
    AssetPortSchema,
    AssetVulnerabilitySchema,
    AssetType,
    AssetCriticality,
    AssetStatus,
)


def test_batch_scan_create_request_valid_raw_targets():
    req = BatchScanCreateRequest(
        raw_targets="192.168.1.1, 192.168.1.2\n10.0.0.1",
        scan_profile=ScanProfile.QUICK,
    )
    assert req.raw_targets == "192.168.1.1, 192.168.1.2\n10.0.0.1"
    assert req.scan_profile == ScanProfile.QUICK


def test_batch_scan_create_request_valid_list():
    req = BatchScanCreateRequest(
        targets=["192.168.1.1", "scanme.nmap.org"],
        scan_profile=ScanProfile.FULL,
    )
    assert isinstance(req.targets, list)
    assert len(req.targets) == 2


def test_batch_scan_create_request_defaults():
    req = BatchScanCreateRequest()
    assert req.targets is None
    assert req.raw_targets is None
    assert req.scan_profile == ScanProfile.QUICK


def test_batch_scan_status_response_serialization():
    item1 = BatchScanItem(
        scan_id="scan-001",
        target="192.168.1.1",
        status=ScanStatus.COMPLETED,
        risk_score=4.5,
    )
    item2 = BatchScanItem(
        scan_id="scan-002",
        target="192.168.1.2",
        status=ScanStatus.RUNNING,
    )

    resp = BatchScanStatusResponse(
        batch_id="batch-123",
        total=2,
        completed=1,
        running=1,
        failed=0,
        pending=0,
        scans=[item1, item2],
    )

    assert resp.batch_id == "batch-123"
    assert resp.total == 2
    assert resp.completed == 1
    assert resp.running == 1
    assert len(resp.scans) == 2
    assert resp.scans[0].status == ScanStatus.COMPLETED


def test_batch_scan_create_response():
    item = BatchScanItem(
        scan_id="scan-abc",
        target="10.0.0.1",
        status=ScanStatus.RUNNING,
    )
    resp = BatchScanCreateResponse(
        batch_id="batch-456",
        total_targets=1,
        created_scans=[item],
        message="Created 1 scan",
    )
    assert resp.batch_id == "batch-456"
    assert len(resp.created_scans) == 1
    assert resp.created_scans[0].scan_id == "scan-abc"


def test_asset_update_request_partial():
    update = AssetUpdateRequest(
        criticality=AssetCriticality.CRITICAL,
        status=AssetStatus.ACTIVE,
        notes="Audit passed",
        tags=["dmz", "gateway"],
    )
    assert update.criticality == AssetCriticality.CRITICAL
    assert update.status == AssetStatus.ACTIVE
    assert update.tags == ["dmz", "gateway"]


def test_asset_detail_response_serialization():
    now = datetime.now(timezone.utc)
    port = AssetPortSchema(
        id=1,
        port=443,
        protocol="tcp",
        service="https",
        version="OpenSSL 3.0",
        last_seen=now,
    )
    vuln = AssetVulnerabilitySchema(
        id=1,
        template_id="ssl-cert-expired",
        name="Expired SSL Certificate",
        severity="medium",
        cvss=5.3,
        cve=None,
        status="open",
        first_seen=now,
        last_seen=now,
    )
    resp = AssetDetailResponse(
        id=101,
        ip_address="192.168.1.50",
        hostname="gw.internal",
        asset_type=AssetType.IP.value,
        criticality=AssetCriticality.HIGH.value,
        status=AssetStatus.ACTIVE.value,
        risk_score=7.2,
        open_ports_count=1,
        vulnerabilities_count=1,
        critical_count=0,
        high_count=0,
        medium_count=1,
        low_count=0,
        ports=[port],
        vulnerabilities=[vuln],
        created_at=now,
        updated_at=now,
    )

    assert resp.id == 101
    assert resp.ip_address == "192.168.1.50"
    assert resp.open_ports_count == 1
    assert len(resp.ports) == 1
    assert resp.ports[0].port == 443
    assert len(resp.vulnerabilities) == 1
    assert resp.vulnerabilities[0].name == "Expired SSL Certificate"


def test_asset_list_response():
    now = datetime.now(timezone.utc)
    asset1 = AssetResponse(
        id=1,
        ip_address="10.0.0.1",
        created_at=now,
        updated_at=now,
    )
    asset_list = AssetListResponse(
        items=[asset1],
        total=1,
        limit=20,
        offset=0,
    )
    assert asset_list.total == 1
    assert len(asset_list.items) == 1


def test_asset_stats_response():
    stats = AssetStatsResponse(
        total_assets=42,
        active_assets=35,
        critical_risk_assets=3,
        total_open_ports=112,
        total_vulnerabilities=29,
        asset_type_distribution={"ip": 20, "domain": 22},
        criticality_distribution={"low": 10, "medium": 21, "high": 8, "critical": 3},
    )
    assert stats.total_assets == 42
    assert stats.asset_type_distribution["ip"] == 20
    assert stats.criticality_distribution["critical"] == 3
