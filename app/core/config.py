# app/core/config.py

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, List
from functools import lru_cache


class Settings(BaseSettings):
    """
    Centralized configuration for XenoraSec.
    All settings can be overridden via environment variables.
    """
    
    # ==================== APPLICATION ====================
    APP_NAME: str = "XenoraSec"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False
    
    # ==================== DATABASE ====================
    DATABASE_URL: str = "sqlite+aiosqlite:///./scans.db"
    # For production with Postgres/Supabase:
    # DATABASE_URL: str = "postgresql+asyncpg://user:pass@host:5432/dbname"
    
    DB_ECHO: bool = False  # Set True for SQL query logging
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    
    # ==================== SCANNING ====================
    MAX_CONCURRENT_SCANS: int = 3
    GLOBAL_SCAN_TIMEOUT: int = 600  # 10 minutes total
    
    # Nmap settings
    NMAP_TIMEOUT: int = 180  # 3 minutes
    NMAP_TIMING: str = "T4"
    NMAP_MAX_RETRIES: int = 2
    
    # Nuclei settings
    NUCLEI_TIMEOUT: int = 300  # 5 minutes
    NUCLEI_RATE_LIMIT: int = 50
    NUCLEI_MAX_RETRIES: int = 1
    MAX_VULNERABILITIES: int = 1000  # Safety cap
    NUCLEI_BUFFER_SIZE: int = 8192
    MAX_BUFFER_SIZE: int = 1048576  # 1MB max buffer
    
    # ==================== SECURITY ====================
    ALLOW_LOCALHOST_SCANNING: bool = False  # Fix 6: Default False — localhost scanning is rarely needed in prod
    ALLOW_PRIVATE_IP_SCANNING: bool = False
    
    # Target restrictions
    TARGET_BLACKLIST: List[str] = Field(default_factory=list)  # e.g., ["military.gov", "192.168.1.1"]
    TARGET_WHITELIST: Optional[List[str]] = None  # If set, only these allowed
    
    MAX_TARGET_LENGTH: int = 253
    
    # ==================== RATE LIMITING ====================
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 10
    RATE_LIMIT_PER_HOUR: int = 100
    
    # ==================== LOGGING ====================
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FORMAT: str = "structured"  # structured or simple
    LOG_FILE: Optional[str] = None  # If set, log to file
    
    # ==================== DATA RETENTION ====================
    SCAN_RETENTION_DAYS: int = 30
    AUTO_CLEANUP_ENABLED: bool = False
    
    # ==================== AI RISK SCORING ====================
    RISK_SCORE_WEIGHTS: dict = Field(default_factory=lambda: {
        "critical": 5.0,
        "high": 3.0,
        "medium": 2.0,
        "low": 1.0,
        "info": 0.5,  # Fixed: Changed from 0.2 to 0.5 to match documentation
        "unknown": 0.5
    })
    
    CVSS_MULTIPLIER: float = 0.15
    OPEN_PORT_FACTOR: float = 0.05
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """
    Cached settings instance.
    Use this function to access settings throughout the app.
    """
    return Settings()


# Convenience accessor
settings = get_settings()