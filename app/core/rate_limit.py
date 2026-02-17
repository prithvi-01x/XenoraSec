# app/core/rate_limit.py

import time
from collections import defaultdict, deque
from typing import Optional, Tuple
from fastapi import Request, HTTPException
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """
    In-memory rate limiter using sliding window algorithm.
    
    ⚠️  WARNING: State is lost on every server restart (e.g. Render cold-starts).
    For production with persistent enforcement, replace with a Redis-backed
    implementation (e.g. fastapi-limiter with aioredis).
    """
    
    def __init__(self):
        # Store request timestamps per IP
        self.requests_per_minute: dict[str, deque] = defaultdict(deque)
        self.requests_per_hour: dict[str, deque] = defaultdict(deque)
        self.last_cleanup = time.time()
    
    def _cleanup_old_entries(self):
        """Periodic cleanup to prevent memory leaks by removing inactive IPs"""
        now = time.time()
        
        # Cleanup every 5 minutes
        if now - self.last_cleanup < 300:
            return
        
        self.last_cleanup = now
        
        # Remove IPs that haven't made requests in the last hour
        cutoff_hour = now - 3600  # 1 hour
        
        # Cleanup per-minute tracking (keep only if has recent timestamps)
        self.requests_per_minute = {
            ip: timestamps 
            for ip, timestamps in self.requests_per_minute.items() 
            if timestamps and timestamps[-1] > cutoff_hour
        }
        
        # Cleanup per-hour tracking (keep only if not empty)
        # We keep hour tracking longer since the window is 1 hour
        self.requests_per_hour = {
            ip: timestamps 
            for ip, timestamps in self.requests_per_hour.items() 
            if timestamps
        }
        
        logger.debug(
            f"Rate limiter cleanup: {len(self.requests_per_minute)} IPs in minute tracking, "
            f"{len(self.requests_per_hour)} IPs in hour tracking"
        )
    
    def _remove_old_timestamps(self, timestamps: deque, window_seconds: int) -> None:
        """Remove timestamps older than the window"""
        now = time.time()
        cutoff = now - window_seconds
        
        while timestamps and timestamps[0] < cutoff:
            timestamps.popleft()
    
    def check_rate_limit(self, client_ip: str) -> Tuple[bool, Optional[str]]:
        """
        Check if request is within rate limits.
        
        Returns:
            (is_allowed, error_message)
        """
        
        if not settings.RATE_LIMIT_ENABLED:
            return True, None
        
        now = time.time()
        
        # Check per-minute limit
        minute_timestamps = self.requests_per_minute[client_ip]
        self._remove_old_timestamps(minute_timestamps, 60)
        
        if len(minute_timestamps) >= settings.RATE_LIMIT_PER_MINUTE:
            logger.warning(f"Rate limit exceeded (minute): {client_ip}")
            return False, f"Rate limit exceeded: {settings.RATE_LIMIT_PER_MINUTE} requests per minute"
        
        # Check per-hour limit
        hour_timestamps = self.requests_per_hour[client_ip]
        self._remove_old_timestamps(hour_timestamps, 3600)
        
        if len(hour_timestamps) >= settings.RATE_LIMIT_PER_HOUR:
            logger.warning(f"Rate limit exceeded (hour): {client_ip}")
            return False, f"Rate limit exceeded: {settings.RATE_LIMIT_PER_HOUR} requests per hour"
        
        # Add current timestamp
        minute_timestamps.append(now)
        hour_timestamps.append(now)
        
        # Periodic cleanup
        self._cleanup_old_entries()
        
        return True, None
    
    def get_client_ip(self, request: Request) -> str:
        """Extract client IP from request.
        
        Uses the LAST entry in X-Forwarded-For, which is appended by the
        trusted reverse proxy (e.g. Render/nginx) and cannot be spoofed by
        a client sending a fake header.
        """
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # Last entry is added by our trusted proxy — cannot be faked
            return forwarded.split(",")[-1].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client
        return request.client.host if request.client else "unknown"


# Global rate limiter instance
rate_limiter = RateLimiter()


async def check_rate_limit(request: Request) -> None:
    """
    FastAPI dependency to enforce rate limiting.
    
    Usage:
        @app.post("/scan", dependencies=[Depends(check_rate_limit)])
    """
    
    client_ip = rate_limiter.get_client_ip(request)
    is_allowed, error_message = rate_limiter.check_rate_limit(client_ip)
    
    if not is_allowed:
        raise HTTPException(
            status_code=429,
            detail=error_message or "Too many requests"
        )