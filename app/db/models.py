# app/db/models.py

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Index, Text
from datetime import datetime, timezone
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
    parent_scan_id = Column(String(36), nullable=True, index=True)
    
    # Error message if failed
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True  # Index for sorting by creation time
    )
    
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
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
            "error_message": self.error_message,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }