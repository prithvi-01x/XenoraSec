# app/schemas/stream.py

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime, UTC
from enum import Enum


class StreamLogLevel(str, Enum):
    """Log severity levels for streaming terminal events"""
    DEBUG = "debug"
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class StreamStage(str, Enum):
    """Scan execution phases"""
    INIT = "init"
    NMAP = "nmap"
    NUCLEI = "nuclei"
    AI = "ai"
    COMPLETE = "complete"
    ERROR = "error"


class ScanLogEvent(BaseModel):
    """Individual real-time terminal log event"""
    scan_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    stage: StreamStage = StreamStage.INIT
    level: StreamLogLevel = StreamLogLevel.INFO
    message: str
    details: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "scan_id": "550e8400-e29b-41d4-a716-446655440000",
                "timestamp": "2026-09-23T12:00:00Z",
                "stage": "nuclei",
                "level": "warning",
                "message": "[CVE-2023-38606] Apple WebKit Vuln matched on https://example.com",
                "details": {"severity": "high", "matched_at": "https://example.com"}
            }
        }
    )


class ScanStreamMessage(BaseModel):
    """Envelope sent across SSE or WebSocket connection"""
    event: str = "log"  # "log", "status", "heartbeat", "done", "error"
    data: ScanLogEvent
