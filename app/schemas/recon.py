# app/schemas/recon.py
"""
Pydantic v2 schemas for Passive Reconnaissance, Certificate Transparency discovery,
DNS intelligence, technology stack fingerprinting, and asset inventory integration.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class SubdomainSource(str, Enum):
    CRTSH = "crtsh"
    CERT_TRANSPARENCY = "cert_transparency"
    PASSIVE_DNS = "passive_dns"
    HACKERTARGET = "hackertarget"
    OTX = "otx"
    MANUAL = "manual"


class SubdomainRecord(BaseModel):
    """Discovered subdomain entity from passive sources."""
    model_config = ConfigDict(from_attributes=True)

    subdomain: str = Field(..., description="Fully qualified domain name of discovered subdomain")
    domain: str = Field(..., description="Root target domain")
    ip_addresses: List[str] = Field(default_factory=list, description="Resolved IPv4/IPv6 addresses")
    cnames: List[str] = Field(default_factory=list, description="Associated CNAME aliases")
    source: str = Field(default="crtsh", description="Passive source that yielded this subdomain")
    is_active: Optional[bool] = Field(default=None, description="Whether subdomain resolves to active IP")
    is_wildcard: bool = Field(default=False, description="Whether record originated from wildcard certificate")
    first_seen: Optional[datetime] = Field(default=None, description="Earliest CT log entry timestamp")
    last_seen: Optional[datetime] = Field(default=None, description="Most recent CT log entry timestamp")
    asn_info: Optional[str] = Field(default=None, description="Autonomous System Name/Number for primary IP")
