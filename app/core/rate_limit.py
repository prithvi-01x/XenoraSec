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
    
    For production, use Redis-backed rate limiting.
    """
    
    def __init__(self):
        # Store request timestamps per IP
        self.requests_per_minute: dict[str, deque] = defaultdict(deque)
        self.requests_per_hour: dict[str, deque] = defaultdict(deque)
        self.last_cleanup = time.time()
    
    def _cleanup_old_entries(self):
        """Periodic cleanup to prevent memory leaks"""
        now = time.time()
        
        # Cleanup every 5 minutes
        if now - self.last_cleanup < 300:
            return
        
        self.last_cleanup = now
        
        # Remove empty deques
        self.requests_per_minute = {
            ip: timestamps 
            for ip, timestamps in self.requests_per_minute.items() 
            if timestamps
        }
        
        self.requests_per_hour = {
            ip: timestamps 
            for ip, timestamps in self.requests_per_hour.items() 
            if timestamps
        }
        
        logger.debug(f"Rate limiter cleanup: {len(self.requests_per_minute)} IPs tracked")
    
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
        """Extract client IP from request"""
        # Check for proxy headers
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
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