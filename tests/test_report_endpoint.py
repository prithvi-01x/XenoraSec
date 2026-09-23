# tests/test_report_endpoint.py

import json
import pytest
from uuid import uuid4
from fastapi.testclient import TestClient

from app.main import app
from app.db.database import AsyncSessionLocal, init_db
from app.db.crud import create_scan, update_scan_result


@pytest.fixture(autouse=True)
async def setup_test_db():
    await init_db()


@pytest.fixture
async def completed_scan_id():
    scan_id = str(uuid4())
    async with AsyncSessionLocal() as db:
        await create_scan(
            db=db,
            scan_id=scan_id,
            target="report-test.example.com",
            scan_profile="full",
            scan_options={"ports": "80,443", "tags": ["cve"]}
        )
        sample_result = {
            "target": "report-test.example.com",
            "status": "completed",
            "risk_score": 7.2,
            "duration": 34.0,
            "scan_profile": "full",
            "nmap": {
                "total_ports": 2,
                "ports": [
                    {"port": 80, "protocol": "tcp", "service": "http", "product": "nginx", "version": "1.20.1"},
                    {"port": 443, "protocol": "tcp", "service": "https", "product": "nginx", "version": "1.20.1"}
                ]
            },
            "nuclei": {
                "vulnerabilities": [
                    {
                        "cve": "CVE-2022-22965",
                        "name": "Spring4Shell RCE",
                        "severity": "critical",
                        "cvss": 9.8,
                        "matched_at": "http://report-test.example.com/helloworld",
                        "description": "Remote code execution via class loader manipulation",
                        "references": ["https://spring.io/blog/2022/03/31/spring-framework-rce-early-announcement"]
                    }
                ]
            },
            "ai_analysis": {
                "executive_summary": "High risk environment with exploitable Spring4Shell entry point."
            }
        }
        await update_scan_result(
            db=db,
            scan_id=scan_id,
            result=sample_result,
            risk_score=7.2,
            duration=34.0,
            status="completed"
        )
    return scan_id


def test_download_report_html(completed_scan_id):
    client = TestClient(app)
    response = client.get(f"/api/scan/{completed_scan_id}/report?format=html")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    assert "<!DOCTYPE html>" in response.text
    assert "report-test.example.com" in response.text
    assert "Spring4Shell" in response.text


def test_download_report_markdown(completed_scan_id):
    client = TestClient(app)
    response = client.get(f"/api/scan/{completed_scan_id}/report?format=markdown&report_type=technical")
    assert response.status_code == 200
    assert "text/markdown" in response.headers.get("content-type", "")
    assert "report-test.example.com" in response.text
    assert "CVE-2022-22965" in response.text
    assert "Content-Disposition" in response.headers


def test_download_report_json(completed_scan_id):
    client = TestClient(app)
    response = client.get(f"/api/scan/{completed_scan_id}/report?format=json")
    assert response.status_code == 200
    assert "application/json" in response.headers.get("content-type", "")
    data = response.json()
    assert data["metadata"]["target"] == "report-test.example.com"
    assert data["metadata"]["scan_profile"] == "full"
    assert len(data["cve_details"]) == 1
    assert data["cve_details"][0]["cve_id"] == "CVE-2022-22965"


def test_download_report_pdf(completed_scan_id):
    client = TestClient(app)
    response = client.get(f"/api/scan/{completed_scan_id}/report?format=pdf&report_type=technical")
    assert response.status_code == 200
    assert "application/pdf" in response.headers.get("content-type", "")
    assert response.content.startswith(b"%PDF-")
    assert len(response.content) > 1000


def test_download_report_nonexistent():
    client = TestClient(app)
    fake_id = str(uuid4())
    response = client.get(f"/api/scan/{fake_id}/report?format=html")
    assert response.status_code == 404
    assert "Scan not found" in response.json().get("detail", "")


def test_download_report_invalid_id():
    client = TestClient(app)
    response = client.get("/api/scan/invalid-uuid-format/report?format=html")
    assert response.status_code == 400


def test_download_report_invalid_format(completed_scan_id):
    client = TestClient(app)
    response = client.get(f"/api/scan/{completed_scan_id}/report?format=invalid_fmt")
    assert response.status_code == 422
