# app/db/models.py

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Index, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
from app.db.database import Base


class ScanResult(Base):
    """
    Database model for scan results.
    
    Status values (unified):
        - running: Scan is in progress
        - completed: Scan finished successfully
        - failed: Scan failed with error
        - partial: Scan completed but with warnings
        - timeout: Scan exceeded time limit
    """
    
    __tablename__ = "scan_results"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Unique scan identifier (UUID from API)
    scan_id = Column(String(36), unique=True, index=True, nullable=False)
    
    # Target information
    target = Column(String(253), index=True, nullable=False)
    
    # Scan status (unified enum)
    status = Column(String(20), nullable=False, index=True)
    
    # Full scan result (nmap + nuclei + analysis)
    result = Column(JSON, nullable=True)
    
    # Calculated risk score (0.0 - 10.0)
    risk_score = Column(Float, default=0.0, nullable=False, index=True)
    
    # Scan duration in seconds
    duration = Column(Float, nullable=True)
    
    # Optional: parent scan_id for retries
    parent_scan_id = Column(String(36), nullable=True)

    # Optional: batch_id for multi-target / CIDR batch scans
    batch_id = Column(String(36), nullable=True, index=True)
    
    # Scan profile and custom options
    scan_profile = Column(String(50), default="quick", nullable=False, index=True)
    scan_options = Column(JSON, nullable=True)
    
    # Error message if failed
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True  # Index for sorting by creation time
    )
    
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
        index=True  # Index for sorting by update time
    )
    
    # Composite indexes for common queries
    __table_args__ = (
        # Index for history queries (status + created_at)
        Index('ix_scan_status_created', 'status', 'created_at'),
        
        # Index for risk-based queries
        Index('ix_scan_risk_created', 'risk_score', 'created_at'),
        
        # Index for target-based queries
        Index('ix_scan_target_created', 'target', 'created_at'),
        
        # Index for parent scan relationships
        Index('ix_scan_parent', 'parent_scan_id'),

        # Index for batch scan queries
        Index('ix_scan_batch_created', 'batch_id', 'created_at'),
    )
    
    def __repr__(self):
        return f"<ScanResult(scan_id={self.scan_id}, target={self.target}, status={self.status})>"
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "scan_id": self.scan_id,
            "target": self.target,
            "status": self.status,
            "result": self.result,
            "risk_score": self.risk_score,
            "duration": self.duration,
            "parent_scan_id": self.parent_scan_id,
            "batch_id": self.batch_id,
            "scan_profile": self.scan_profile,
            "scan_options": self.scan_options,
            "error_message": self.error_message,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class Asset(Base):
    """
    Asset Inventory model for tracking scanned targets, hosts, domains,
    along with aggregated vulnerability counts and security posture.
    """
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ip_address = Column(String(100), index=True, nullable=False)
    hostname = Column(String(255), index=True, nullable=True)
    asset_type = Column(String(50), default="ip", nullable=False, index=True)
    status = Column(String(50), default="active", nullable=False, index=True)
    criticality = Column(String(50), default="medium", nullable=False)
    risk_score = Column(Float, default=0.0, nullable=False, index=True)

    open_ports_count = Column(Integer, default=0, nullable=False)
    vulnerabilities_count = Column(Integer, default=0, nullable=False)
    critical_count = Column(Integer, default=0, nullable=False)
    high_count = Column(Integer, default=0, nullable=False)
    medium_count = Column(Integer, default=0, nullable=False)
    low_count = Column(Integer, default=0, nullable=False)

    tags = Column(JSON, nullable=True)
    notes = Column(Text, nullable=True)
    last_scanned_at = Column(DateTime, nullable=True)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False
    )

    ports = relationship("AssetPort", back_populates="asset", cascade="all, delete-orphan", lazy="selectin")
    vulnerabilities = relationship("AssetVulnerability", back_populates="asset", cascade="all, delete-orphan", lazy="selectin")

    __table_args__ = (
        Index('ix_asset_ip_host', 'ip_address', 'hostname'),
        Index('ix_asset_risk_type', 'risk_score', 'asset_type'),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "ip_address": self.ip_address,
            "hostname": self.hostname,
            "asset_type": self.asset_type,
            "status": self.status,
            "criticality": self.criticality,
            "risk_score": self.risk_score,
            "open_ports_count": self.open_ports_count,
            "vulnerabilities_count": self.vulnerabilities_count,
            "critical_count": self.critical_count,
            "high_count": self.high_count,
            "medium_count": self.medium_count,
            "low_count": self.low_count,
            "tags": self.tags or [],
            "notes": self.notes,
            "last_scanned_at": self.last_scanned_at,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class AssetPort(Base):
    """Discovered open port associated with an asset."""
    __tablename__ = "asset_ports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    asset_id = Column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    port = Column(Integer, nullable=False, index=True)
    protocol = Column(String(20), default="tcp", nullable=False)
    service = Column(String(100), nullable=True)
    product = Column(String(100), nullable=True)
    version = Column(String(100), nullable=True)
    last_seen = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    asset = relationship("Asset", back_populates="ports")

    __table_args__ = (
        Index('ix_asset_port_unique', 'asset_id', 'port', 'protocol', unique=True),
    )


class AssetVulnerability(Base):
    """Vulnerability finding associated with an asset."""
    __tablename__ = "asset_vulnerabilities"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    asset_id = Column(Integer, ForeignKey("assets.id", ondelete="CASCADE"), nullable=False, index=True)
    template_id = Column(String(255), nullable=True, index=True)
    name = Column(String(255), nullable=False)
    severity = Column(String(50), nullable=False, index=True)
    cve = Column(String(100), nullable=True, index=True)
    cvss = Column(Float, nullable=True)
    matched_at = Column(Text, nullable=True)
    status = Column(String(50), default="open", nullable=False)
    first_seen = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    last_seen = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)

    asset = relationship("Asset", back_populates="vulnerabilities")

    __table_args__ = (
        Index('ix_asset_vuln_unique', 'asset_id', 'template_id', 'name'),
    )