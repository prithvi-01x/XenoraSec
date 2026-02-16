# app/core/security.py

import re
import ipaddress
from typing import Tuple, Optional
from urllib.parse import urlparse
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class TargetValidationError(Exception):
    """Raised when target validation fails"""
    pass


def is_private_ip(ip: str) -> bool:
    """Check if IP address is private/internal"""
    try:
        ip_obj = ipaddress.ip_address(ip)
        return ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local
    except ValueError:
        return False


def extract_hostname(target: str) -> Tuple[str, Optional[str]]:
    """
    Extract hostname/IP from target, handling URLs.
    
    Returns:
        (hostname, scheme) - hostname for scanning, original scheme if URL
    """
    target = target.strip()
    
    # If it starts with http:// or https://, parse as URL
    if target.startswith(("http://", "https://")):
        parsed = urlparse(target)
        return parsed.hostname or parsed.netloc, parsed.scheme
    
    # Otherwise treat as hostname/IP
    return target, None


def validate_target(
    target: str, 
    allow_private: Optional[bool] = None,
    allow_localhost: Optional[bool] = None
) -> Tuple[bool, Optional[str], dict]:
    """
    Comprehensive target validation.
    
    Returns:
        (is_valid, error_message, metadata)
        metadata: {"hostname": str, "scheme": str, "is_ip": bool, "is_private": bool}
    """
    
    # Use provided overrides or global settings
    allow_private = allow_private if allow_private is not None else settings.ALLOW_PRIVATE_IP_SCANNING
    allow_localhost = allow_localhost if allow_localhost is not None else settings.ALLOW_LOCALHOST_SCANNING
    
    if not target or not isinstance(target, str):
        return False, "Target must be a non-empty string", {}
    
    target = target.strip()
    
    # Length check
    if len(target) > settings.MAX_TARGET_LENGTH:
        return False, f"Target exceeds maximum length ({settings.MAX_TARGET_LENGTH})", {}
    
    # Extract hostname
    hostname, scheme = extract_hostname(target)
    
    if not hostname:
        return False, "Could not extract hostname from target", {}
    
    metadata = {
        "hostname": hostname,
        "scheme": scheme,
        "is_ip": False,
        "is_private": False,
        "original_target": target
    }
    
    # Validate as IP address
    is_valid_ip, ip_error = validate_ip_address(hostname)
    
    if is_valid_ip:
        metadata["is_ip"] = True
        metadata["is_private"] = is_private_ip(hostname)
        
        # Check private IP restrictions
        if metadata["is_private"]:
            if not allow_private:
                # Still block if it's literally localhost and local scanning is off
                if (hostname.startswith("127.") or hostname == "localhost"):
                    if not allow_localhost:
                        return False, "Scanning localhost is not allowed", metadata
                else:
                    return False, "Scanning private IP addresses is not allowed", metadata
            
            # Allow localhost if configured
            if hostname.startswith("127.") or hostname == "localhost":
                if not allow_localhost:
                    return False, "Scanning localhost is not allowed", metadata
    
    else:
        # Validate as domain
        is_valid_domain, domain_error = validate_domain(hostname)
        
        if not is_valid_domain:
            return False, domain_error or "Invalid domain format", metadata
    
    # Check blacklist
    if settings.TARGET_BLACKLIST:
        for blocked in settings.TARGET_BLACKLIST:
            if blocked in hostname:
                logger.warning(f"Blocked target attempted: {target}")
                return False, "Target is blacklisted", metadata
    
    # Check whitelist (if enabled)
    if settings.TARGET_WHITELIST:
        allowed = False
        for allowed_target in settings.TARGET_WHITELIST:
            if allowed_target in hostname:
                allowed = True
                break
        
        if not allowed:
            return False, "Target not in whitelist", metadata
    
    return True, None, metadata


def validate_ip_address(ip: str) -> Tuple[bool, Optional[str]]:
    """Validate IP address (v4 or v6)"""
    try:
        ipaddress.ip_address(ip)
        return True, None
    except ValueError as e:
        return False, str(e)


def validate_domain(domain: str) -> Tuple[bool, Optional[str]]:
    """Validate domain name format"""
    
    if not domain:
        return False, "Domain is empty"
    
    # Basic domain pattern
    domain_pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z]{2,}$'
    
    # Allow localhost
    if domain == "localhost":
        return True, None
    
    if not re.match(domain_pattern, domain):
        return False, "Invalid domain format"
    
    # Check for valid TLD
    parts = domain.split(".")
    if len(parts) < 2:
        return False, "Domain must have at least one dot"
    
    return True, None


def prepare_nmap_target(target: str, metadata: dict) -> str:
    """
    Prepare target for Nmap (strip URL schemes).
    Nmap only accepts hostnames/IPs, not URLs.
    """
    return metadata.get("hostname", target)


def prepare_nuclei_target(target: str, metadata: dict) -> str:
    """
    Prepare target for Nuclei (ensure URL format).
    Nuclei requires full URLs with scheme.
    """
    hostname = metadata.get("hostname", target)
    scheme = metadata.get("scheme")
    
    # If original had a scheme, use it
    if scheme:
        return f"{scheme}://{hostname}"
    
    # Otherwise default to http://
    return f"http://{hostname}"


def sanitize_scan_id(scan_id: str) -> str:
    """Sanitize scan_id to prevent injection"""
    # UUIDs should only contain alphanumeric and hyphens
    if not re.match(r'^[a-f0-9\-]{36}$', scan_id):
        raise TargetValidationError("Invalid scan_id format")
    return scan_id