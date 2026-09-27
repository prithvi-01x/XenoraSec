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


class DNSRecordType(str, Enum):
    A = "A"
    AAAA = "AAAA"
    CNAME = "CNAME"
    MX = "MX"
    TXT = "TXT"
    NS = "NS"
    PTR = "PTR"
    SOA = "SOA"


class DNSRecord(BaseModel):
    """Normalized DNS resource record."""
    model_config = ConfigDict(from_attributes=True)

    record_type: str = Field(..., description="DNS record classification (A, MX, TXT, etc.)")
    host: str = Field(..., description="Host domain name queried")
    value: str = Field(..., description="Resolved value or target address")
    ttl: Optional[int] = Field(default=None, description="Time to live in seconds")
    priority: Optional[int] = Field(default=None, description="Priority for MX or SRV records")


class MailSecurityPosture(BaseModel):
    """Email hygiene and spoofing protection configuration."""
    model_config = ConfigDict(from_attributes=True)

    has_spf: bool = Field(default=False, description="Sender Policy Framework record exists")
    spf_record: Optional[str] = Field(default=None, description="Raw SPF TXT record string")
    spf_status: str = Field(default="missing", description="SPF validation status (pass, weak, missing)")
    has_dmarc: bool = Field(default=False, description="DMARC policy record exists")
    dmarc_record: Optional[str] = Field(default=None, description="Raw DMARC TXT record string")
    dmarc_policy: Optional[str] = Field(default="missing", description="Policy enforcement (reject, quarantine, none, missing)")
    has_dkim_indicator: bool = Field(default=False, description="DKIM selector discovery hints present")
    security_rating: str = Field(default="insecure", description="Overall mail authentication grade (secure, warning, insecure)")


class DNSIntelligence(BaseModel):
    """Comprehensive DNS map and topology evaluation."""
    model_config = ConfigDict(from_attributes=True)

    domain: str = Field(..., description="Base domain evaluated")
    records: List[DNSRecord] = Field(default_factory=list, description="All discovered DNS records")
    nameservers: List[str] = Field(default_factory=list, description="Authoritative nameservers")
    mail_servers: List[str] = Field(default_factory=list, description="Configured MX mail exchangers")
    ipv4_addresses: List[str] = Field(default_factory=list, description="A record addresses")
    ipv6_addresses: List[str] = Field(default_factory=list, description="AAAA record addresses")
    cname_records: List[str] = Field(default_factory=list, description="CNAME targets")
    txt_records: List[str] = Field(default_factory=list, description="TXT record entries")
    reverse_dns: Dict[str, str] = Field(default_factory=dict, description="Reverse PTR mappings (IP -> Hostname)")
    mail_security: Optional[MailSecurityPosture] = Field(default=None, description="Email spoofing posture analysis")
    asn_details: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="BGP Autonomous System details per IP")
