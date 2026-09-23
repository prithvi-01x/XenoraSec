# app/schemas/report.py

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ReportFormat(str, Enum):
    """Supported report export formats"""
    JSON = "json"
    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"


class ReportType(str, Enum):
    """Report audience type"""
    TECHNICAL = "technical"
    EXECUTIVE = "executive"


class ReportMetadata(BaseModel):
    """Metadata regarding a generated report"""
    report_id: str
    scan_id: str
    target: str
    generated_at: datetime
    report_type: ReportType
    format: ReportFormat
    author: str = "XenoraSec Security Engine"
    organization: str = "XenoraSec"
    risk_score: float = 0.0


class ExecutiveSummary(BaseModel):
    """High-level summary tailored for executive leadership"""
    target: str
    scan_date: datetime
    overall_risk: float
    risk_category: str
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    info_count: int
    open_ports_count: int
    key_findings: List[str] = Field(default_factory=list)
    strategic_recommendations: List[str] = Field(default_factory=list)


class CveDetail(BaseModel):
    """Detailed CVE information extracted from scan findings"""
    cve_id: str
    title: str
    severity: str
    cvss_score: Optional[float] = None
    cwe_id: Optional[str] = None
    affected_target: str
    description: Optional[str] = None
    remediation_advice: Optional[str] = None
    references: List[str] = Field(default_factory=list)


class RemediationAdvice(BaseModel):
    """Actionable remediation guidance per finding category"""
    title: str
    severity: str
    affected_hosts: List[str] = Field(default_factory=list)
    guidance: str
    priority: str
    references: List[str] = Field(default_factory=list)


class ReportDownloadResponse(BaseModel):
    """Response containing report download details"""
    scan_id: str
    format: ReportFormat
    report_type: ReportType
    filename: str
    size_bytes: int
    download_url: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "scan_id": "550e8400-e29b-41d4-a716-446655440000",
                "format": "pdf",
                "report_type": "technical",
                "filename": "xenorasec-report-550e8400-technical.pdf",
                "size_bytes": 104230,
                "download_url": "/api/scan/550e8400-e29b-41d4-a716-446655440000/report?format=pdf&report_type=technical"
            }
        }
    )
