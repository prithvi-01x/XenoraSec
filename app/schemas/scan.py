# app/schemas/scan.py

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ==================== ENUMS ====================

class ScanStatus(str, Enum):
    """
    Unified scan status enum used across DB, services, and API.
    """
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"
    TIMEOUT = "timeout"


class SeverityLevel(str, Enum):
    """Vulnerability severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"
    UNKNOWN = "unknown"


class ScanProfile(str, Enum):
    """Scan profile types"""
    QUICK = "quick"
    FULL = "full"
    NETWORK = "network"
    CUSTOM = "custom"


# Import and re-export to maintain single source of truth without breaking backwards compatibility
from app.schemas.report import ReportFormat, ReportType


# ==================== REQUEST SCHEMAS ====================

class ScanOptions(BaseModel):
    """Optional scan configuration overrides"""
    profile: Optional[ScanProfile] = ScanProfile.QUICK
    port_range: Optional[str] = "1-1000"
    nmap_timing: Optional[str] = "T4"
    nuclei_tags: Optional[List[str]] = Field(
        default_factory=lambda: ["cve", "misconfig", "exposure"]
    )
    nuclei_templates: Optional[List[str]] = None
    severity_filter: Optional[List[str]] = None
    concurrency: Optional[int] = 10
    timeout_minutes: Optional[int] = 30
    rate_limit: Optional[int] = 100
    allow_private: bool = Field(
        default=False,
        description="Allow scanning of private IP addresses (must be globally enabled)"
    )
    allow_localhost: bool = Field(
        default=True,
        description="Allow scanning of localhost/127.0.0.1"
    )

class ScanCreateRequest(BaseModel):
    """Request to create a new scan"""
    target: str = Field(
        ...,
        description="Target hostname, IP, or URL to scan",
        min_length=1,
        max_length=253
    )
    scan_profile: Optional[ScanProfile] = ScanProfile.QUICK
    scan_mode: Optional[str] = "quick"  # Backward compatibility
    options: Optional[ScanOptions] = None

    @field_validator("target")
    @classmethod
    def validate_target_format(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Target cannot be empty")
        return v.strip()


class ReportRequest(BaseModel):
    """Request parameters for generating reports"""
    format: ReportFormat = ReportFormat.HTML
    report_type: ReportType = ReportType.TECHNICAL
    include_remediation: bool = True
    include_raw_output: bool = False


# ==================== RESPONSE SCHEMAS ====================

class ScanCreateResponse(BaseModel):
    """Response after creating a scan"""
    scan_id: str
    target: str
    status: ScanStatus
    scan_profile: Optional[str] = "quick"
    message: str = "Scan started successfully"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "scan_id": "550e8400-e29b-41d4-a716-446655440000",
                "target": "example.com",
                "status": "running",
                "scan_profile": "quick",
                "message": "Scan started successfully"
            }
        }
    )


class PortInfo(BaseModel):
    port: int
    protocol: str
    service: Optional[str] = None
    product: Optional[str] = None
    version: Optional[str] = None


class VulnerabilityInfo(BaseModel):
    template_id: Optional[str] = None
    name: Optional[str] = None
    severity: str
    matched_at: Optional[str] = None
    description: Optional[str] = None
    cve: Optional[str] = None
    cvss: Optional[float] = None
    cwe: Optional[str] = None
    references: Optional[List[str]] = None
    tags: Optional[List[str]] = None

    @field_validator('cve', 'cwe', mode='before')
    @classmethod
    def convert_list_to_string(cls, v):
        """Convert list values to comma-separated strings (Nuclei returns lists)"""
        if isinstance(v, list):
            return ', '.join(str(x) for x in v) if v else None
        return v


class ScanSummary(BaseModel):
    total_vulnerabilities: int
    open_ports: int
    severity_distribution: Dict[str, int]
    critical_count: int
    high_count: int


class NmapResult(BaseModel):
    status: str
    target: str
    host_info: Optional[Dict[str, Any]] = None
    ports: List[PortInfo] = Field(default_factory=list)
    total_ports: int
    error: Optional[str] = None


class NucleiResult(BaseModel):
    status: str
    target: str
    vulnerabilities: List[VulnerabilityInfo] = Field(default_factory=list)
    total_vulnerabilities: int
    severity_distribution: Dict[str, int]
    scan_stats: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ScanResultResponse(BaseModel):
    scan_id: str
    target: str
    status: ScanStatus
    scan_profile: Optional[str] = "quick"
    scan_options: Optional[Dict[str, Any]] = None
    risk_score: float
    duration: Optional[float] = None
    summary: ScanSummary
    nmap: NmapResult
    nuclei: NucleiResult
    created_at: datetime
    updated_at: datetime
    error: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "scan_id": "550e8400-e29b-41d4-a716-446655440000",
                "target": "example.com",
                "status": "completed",
                "scan_profile": "quick",
                "risk_score": 7.5,
                "duration": 45.2,
                "summary": {
                    "total_vulnerabilities": 5,
                    "open_ports": 3,
                    "severity_distribution": {"high": 2, "medium": 3},
                    "critical_count": 0,
                    "high_count": 2
                },
                "nmap": {
                    "status": "completed",
                    "target": "example.com",
                    "host_info": None,
                    "ports": [],
                    "total_ports": 0,
                    "error": None
                },
                "nuclei": {
                    "status": "completed",
                    "target": "example.com",
                    "vulnerabilities": [],
                    "total_vulnerabilities": 0,
                    "severity_distribution": {},
                    "scan_stats": None,
                    "error": None
                },
                "created_at": "2024-01-01T12:00:00Z",
                "updated_at": "2024-01-01T12:01:00Z"
            }
        }
    )


class ScanHistoryItem(BaseModel):
    scan_id: str
    target: str
    status: ScanStatus
    scan_profile: Optional[str] = "quick"
    risk_score: float
    created_at: datetime
    updated_at: datetime
    duration: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class ScanHistoryResponse(BaseModel):
    items: List[ScanHistoryItem]
    total: int
    limit: int
    offset: int

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "scan_id": "550e8400-e29b-41d4-a716-446655440000",
                        "target": "example.com",
                        "status": "completed",
                        "risk_score": 7.5,
                        "created_at": "2024-01-01T12:00:00Z",
                        "updated_at": "2024-01-01T12:01:00Z"
                    }
                ],
                "total": 100,
                "limit": 10,
                "offset": 0
            }
        }
    )


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str
    timestamp: datetime
    database: str = "connected"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "ok",
                "version": "2.0.0",
                "timestamp": "2024-01-01T12:00:00Z",
                "database": "connected"
            }
        }
    )


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "detail": "Scan not found",
                "error_code": "SCAN_NOT_FOUND"
            }
        }
    )
