# tests/test_schemas.py

import pytest
from app.schemas.scan import (
    ScanProfile,
    ScanOptions,
    ScanCreateRequest,
    ScanCreateResponse,
    ScanResultResponse,
    ScanStatus,
    ReportFormat,
    ReportType,
)
from app.schemas.report import (
    ReportMetadata,
    ExecutiveSummary,
    CveDetail,
    RemediationAdvice,
)
from app.schemas.stream import (
    ScanLogEvent,
    ScanStreamMessage,
    StreamLogLevel,
    StreamStage,
)
from datetime import datetime, UTC


def test_scan_profile_enum():
    assert ScanProfile.QUICK == "quick"
    assert ScanProfile.FULL == "full"
    assert ScanProfile.NETWORK == "network"
    assert ScanProfile.CUSTOM == "custom"


def test_scan_options_defaults():
    opts = ScanOptions()
    assert opts.profile == ScanProfile.QUICK
    assert opts.port_range == "1-1000"
    assert opts.nmap_timing == "T4"
    assert "cve" in opts.nuclei_tags
    assert "misconfig" in opts.nuclei_tags


def test_scan_create_request_with_profile():
    req = ScanCreateRequest(
        target="example.com",
        scan_profile=ScanProfile.FULL,
        options=ScanOptions(
            profile=ScanProfile.FULL,
            port_range="80,443,8080",
            nuclei_tags=["cve", "rce"]
        )
    )
    assert req.target == "example.com"
    assert req.scan_profile == ScanProfile.FULL
    assert req.options.port_range == "80,443,8080"
    assert req.options.nuclei_tags == ["cve", "rce"]


def test_report_schemas():
    meta = ReportMetadata(
        report_id="rep-123",
        scan_id="scan-456",
        target="example.com",
        generated_at=datetime.now(UTC),
        report_type=ReportType.TECHNICAL,
        format=ReportFormat.HTML,
        risk_score=6.5
    )
    assert meta.report_id == "rep-123"
    assert meta.report_type == ReportType.TECHNICAL
    assert meta.format == ReportFormat.HTML

    summary = ExecutiveSummary(
        target="example.com",
        scan_date=datetime.now(UTC),
        overall_risk=8.0,
        risk_category="High",
        critical_count=1,
        high_count=2,
        medium_count=1,
        low_count=0,
        info_count=3,
        open_ports_count=4,
        key_findings=["Critical CVE-2023-1234 detected"],
        strategic_recommendations=["Patch immediately"]
    )
    assert summary.critical_count == 1
    assert len(summary.key_findings) == 1


def test_stream_log_event_schema():
    event = ScanLogEvent(
        scan_id="scan-999",
        stage=StreamStage.NMAP,
        level=StreamLogLevel.INFO,
        message="Port 443/tcp open"
    )
    msg = ScanStreamMessage(event="log", data=event)
    assert msg.event == "log"
    assert msg.data.stage == StreamStage.NMAP
    assert msg.data.message == "Port 443/tcp open"
