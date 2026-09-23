import json
import pytest
from datetime import datetime, UTC
from app.schemas.report import ReportFormat, ReportType
from app.services.report_service import (
    generate_executive_summary,
    extract_cve_details,
    generate_json_report,
    generate_markdown_report,
    generate_html_report,
    generate_pdf_report,
)


@pytest.fixture
def sample_scan_data():
    return {
        "scan_id": "test-uuid-1234-5678",
        "target": "scanme.nmap.org",
        "status": "completed",
        "scan_profile": "full",
        "risk_score": 8.5,
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
        "duration": 42.5,
        "nmap": {
            "ports": [
                {
                    "port": 80,
                    "protocol": "tcp",
                    "service": "http",
                    "product": "Apache httpd",
                    "version": "2.4.41",
                    "extrainfo": "Ubuntu"
                },
                {
                    "port": 22,
                    "protocol": "tcp",
                    "service": "ssh",
                    "product": "OpenSSH",
                    "version": "8.2p1",
                    "extrainfo": "Ubuntu"
                }
            ]
        },
        "nuclei": {
            "vulnerabilities": [
                {
                    "cve": "CVE-2021-41773",
                    "name": "Apache Path Traversal RCE",
                    "severity": "critical",
                    "cvss": 9.8,
                    "cwe": "CWE-22",
                    "matched_at": "http://scanme.nmap.org/icons/.%2e/%2e%2e/%2e%2e/etc/passwd",
                    "description": "Path traversal and remote code execution in Apache 2.4.49",
                    "references": ["https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2021-41773"]
                },
                {
                    "cve": "CVE-2020-1938",
                    "name": "Apache Ghostcat File Read",
                    "severity": "high",
                    "cvss": 7.5,
                    "cwe": "CWE-200",
                    "matched_at": "scanme.nmap.org:8009",
                    "description": "Tomcat AJP protocol arbitrary file read/inclusion",
                    "references": ["https://nvd.nist.gov/vuln/detail/CVE-2020-1938"]
                }
            ]
        },
        "ai_analysis": {
            "executive_summary": "Target exhibits critical edge exposures requiring immediate patch management."
        },
        "scan_options": {
            "tags": ["cve", "rce"]
        }
    }


def test_generate_executive_summary(sample_scan_data):
    summary = generate_executive_summary(sample_scan_data)
    assert summary.critical_count == 1
    assert summary.high_count == 1
    assert summary.open_ports_count == 2
    assert "Critical" in summary.risk_category
    assert len(summary.key_findings) > 0
    assert len(summary.strategic_recommendations) > 0


def test_extract_cve_details(sample_scan_data):
    cves = extract_cve_details(sample_scan_data["nuclei"], sample_scan_data["target"])
    assert len(cves) == 2
    cve_ids = [c.cve_id for c in cves]
    assert "CVE-2021-41773" in cve_ids
    assert "CVE-2020-1938" in cve_ids
    for c in cves:
        assert c.remediation_advice != ""
        assert c.severity in ["critical", "high"]


def test_generate_json_report(sample_scan_data):
    report_str = generate_json_report(sample_scan_data, ReportType.TECHNICAL)
    assert isinstance(report_str, str)
    data = json.loads(report_str)
    assert data["metadata"]["target"] == "scanme.nmap.org"
    assert data["metadata"]["scan_profile"] == "full"
    assert data["executive_summary"]["critical_count"] == 1
    assert len(data["cve_details"]) == 2
    assert len(data["network_perimeter"]["ports"]) == 2


def test_generate_markdown_report_technical(sample_scan_data):
    md = generate_markdown_report(sample_scan_data, ReportType.TECHNICAL)
    assert "Technical Vulnerability Assessment Report" in md
    assert "Target System:" in md
    assert "CVE-2021-41773" in md
    assert "Apache Path Traversal RCE" in md
    assert "80/tcp" in md
    assert "Key Findings" in md


def test_generate_markdown_report_executive(sample_scan_data):
    md = generate_markdown_report(sample_scan_data, ReportType.EXECUTIVE)
    assert "Executive Security Posture Brief" in md
    assert "Executive Summary" in md
    assert "Strategic Remediation Recommendations" in md
    # Executive report omits raw port table
    assert "Perimeter Port & Service Discovery" not in md


def test_generate_html_report(sample_scan_data):
    html = generate_html_report(sample_scan_data, ReportType.TECHNICAL)
    assert "<!DOCTYPE html>" in html
    assert "scanme.nmap.org" in html
    assert "CVE-2021-41773" in html
    assert "@media print" in html
    assert "80/tcp" in html


def test_generate_pdf_report_technical(sample_scan_data):
    pdf = generate_pdf_report(sample_scan_data, ReportType.TECHNICAL)
    assert isinstance(pdf, bytes)
    assert pdf.startswith(b"%PDF-")
    assert len(pdf) > 1000


def test_generate_pdf_report_executive(sample_scan_data):
    pdf = generate_pdf_report(sample_scan_data, ReportType.EXECUTIVE)
    assert isinstance(pdf, bytes)
    assert pdf.startswith(b"%PDF-")
    assert len(pdf) > 1000


def test_reports_with_empty_scan():
    empty_scan = {
        "scan_id": "empty-1",
        "target": "clean.internal",
        "status": "completed",
        "risk_score": 0.0
    }
    json_rep = generate_json_report(empty_scan, ReportType.TECHNICAL)
    data = json.loads(json_rep)
    assert "Minimal" in data["executive_summary"]["risk_category"]
    assert len(data["cve_details"]) == 0

    md = generate_markdown_report(empty_scan, ReportType.TECHNICAL)
    assert "No high or critical vulnerabilities" in md

    html = generate_html_report(empty_scan, ReportType.TECHNICAL)
    assert "clean.internal" in html

    pdf = generate_pdf_report(empty_scan, ReportType.TECHNICAL)
    assert pdf.startswith(b"%PDF-")
