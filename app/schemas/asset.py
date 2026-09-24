# app/schemas/asset.py

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class AssetType(str, Enum):
    IP = "ip"
    DOMAIN = "domain"
    URL = "url"
    CIDR_HOST = "cidr_host"


class AssetCriticality(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AssetStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SCANNED = "scanned"
    DECOMMISSIONED = "decommissioned"


class AssetPortSchema(BaseModel):
    id: Optional[int] = None
    port: int
    protocol: str = "tcp"
    service: Optional[str] = None
    product: Optional[str] = None
    version: Optional[str] = None
    last_seen: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AssetVulnerabilitySchema(BaseModel):
    id: Optional[int] = None
    template_id: Optional[str] = None
    name: str
    severity: str
    cve: Optional[str] = None
    cvss: Optional[float] = None
    matched_at: Optional[str] = None
    status: str = "open"
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class AssetResponse(BaseModel):
    id: int
    ip_address: str
    hostname: Optional[str] = None
    asset_type: str = "ip"
    status: str = "active"
    criticality: str = "medium"
    risk_score: float = 0.0
    open_ports_count: int = 0
    vulnerabilities_count: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    tags: Optional[List[str]] = Field(default_factory=list)
    notes: Optional[str] = None
    last_scanned_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AssetDetailResponse(AssetResponse):
    ports: List[AssetPortSchema] = Field(default_factory=list)
    vulnerabilities: List[AssetVulnerabilitySchema] = Field(default_factory=list)


class AssetListResponse(BaseModel):
    items: List[AssetResponse]
    total: int
    limit: int
    offset: int


class AssetStatsResponse(BaseModel):
    total_assets: int
    active_assets: int
    critical_risk_assets: int
    total_open_ports: int
    total_vulnerabilities: int
    asset_type_distribution: Dict[str, int] = Field(default_factory=dict)
    criticality_distribution: Dict[str, int] = Field(default_factory=dict)


class AssetUpdateRequest(BaseModel):
    criticality: Optional[AssetCriticality] = None
    status: Optional[AssetStatus] = None
    tags: Optional[List[str]] = None
    notes: Optional[str] = None
