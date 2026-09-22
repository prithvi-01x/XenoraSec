# app/core/security.py

import re
import socket
import ipaddress
from typing import Tuple, Optional, List
from urllib.parse import urlparse
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class TargetValidationError(Exception):
    """Raised when target validation fails"""
    pass


def is_loopback_ip(ip: str) -> bool:
    """Check if IP address is loopback / 127.x.x.x / ::1 / 0.0.0.0"""
    try:
        ip_obj = ipaddress.ip_address(ip)
        return ip_obj.is_loopback or str(ip_obj) in ("0.0.0.0", "::")
    except ValueError:
        return False


def is_private_ip(ip: str) -> bool:
    """Check if IP address is private, internal, link-local, or reserved"""
    try:
        ip_obj = ipaddress.ip_address(ip)
        return (
            ip_obj.is_private
            or ip_obj.is_loopback
            or ip_obj.is_link_local
            or ip_obj.is_reserved
            or ip_obj.is_multicast
            or ip_obj.is_unspecified
        )
    except ValueError:
        return False


def resolve_hostname_ips(hostname: str) -> List[str]:
    """
    Resolve a hostname or domain to its associated unique IP addresses.
    Returns empty list if DNS resolution fails.
    """
    if hostname.lower() == "localhost" or hostname.lower().endswith(".localhost"):
        return ["127.0.0.1"]
    try:
        addr_info = socket.getaddrinfo(hostname, None)
        # Deduplicate resolved IP addresses preserving order
        ips = list(dict.fromkeys(info[4][0] for info in addr_info if info[4]))
        return ips
    except (socket.gaierror, socket.herror, Exception) as e:
        logger.debug(f"DNS resolution failed for hostname '{hostname}': {e}")
        return []


def extract_hostname(target: str) -> Tuple[str, Optional[str]]:
    """
    Extract hostname/IP from target, handling URLs.
    
    Returns:
        (hostname, scheme) - hostname for scanning, original scheme if URL
    """
    target = target.strip()
    
    # If it starts with http:// or https:// (case-insensitive), parse as URL
    if target.lower().startswith(("http://", "https://")):
        parsed = urlparse(target)
        host = parsed.hostname or parsed.netloc
        if host and host.startswith("[") and host.endswith("]"):
            host = host[1:-1]
        return host, parsed.scheme.lower()
    
    # Handle bare bracketed IPv6 (e.g. [::1])
    if target.startswith("[") and "]" in target:
        end_idx = target.find("]")
        return target[1:end_idx], None

    # Otherwise treat as hostname/IP
    return target, None


def validate_target(
    target: str, 
    allow_private: Optional[bool] = None,
    allow_localhost: Optional[bool] = None
) -> Tuple[bool, Optional[str], dict]:
    """
    Comprehensive target validation including SSRF protection,
    localhost filtering, and DNS resolution validation.
    
    Returns:
        (is_valid, error_message, metadata)
        metadata: {"hostname": str, "scheme": str, "netloc": str, "path": str, "is_ip": bool, "is_private": bool, "resolved_ips": List[str]}
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
    
    hostname_clean = hostname.strip().lower()
    
    netloc = None
    url_path = None
    if target.lower().startswith(("http://", "https://")):
        parsed_url = urlparse(target)
        netloc = parsed_url.netloc
        url_path = parsed_url.path

    metadata = {
        "hostname": hostname,
        "scheme": scheme,
        "netloc": netloc,
        "path": url_path,
        "is_ip": False,
        "is_private": False,
        "resolved_ips": [],
        "original_target": target
    }
    
    # Check explicit localhost hostnames first
    if hostname_clean == "localhost" or hostname_clean.endswith(".localhost"):
        metadata["is_private"] = True
        metadata["resolved_ips"] = ["127.0.0.1"]
        if not allow_localhost:
            return False, "Scanning localhost is not allowed", metadata
    else:
        # Validate as IP address
        is_valid_ip, ip_error = validate_ip_address(hostname)
        
        if is_valid_ip:
            metadata["is_ip"] = True
            metadata["resolved_ips"] = [hostname]
            
            # Check loopback / localhost
            if is_loopback_ip(hostname):
                metadata["is_private"] = True
                if not allow_localhost:
                    return False, "Scanning localhost is not allowed", metadata
            elif is_private_ip(hostname):
                metadata["is_private"] = True
                if not allow_private:
                    return False, "Scanning private IP addresses is not allowed", metadata
        else:
            # Validate as domain name
            is_valid_domain, domain_error = validate_domain(hostname)
            if not is_valid_domain:
                return False, domain_error or "Invalid domain format", metadata
            
            # Resolve domain to IP addresses to prevent SSRF / DNS rebinding bypasses
            resolved_ips = resolve_hostname_ips(hostname)
            if not resolved_ips:
                return False, f"Could not resolve domain '{hostname}' via DNS", metadata
            
            metadata["resolved_ips"] = resolved_ips
            
            # Verify all resolved IPs against security restrictions
            for resolved_ip in resolved_ips:
                if is_loopback_ip(resolved_ip):
                    metadata["is_private"] = True
                    if not allow_localhost:
                        return False, f"Domain '{hostname}' resolves to loopback IP ({resolved_ip}), which is not allowed", metadata
                elif is_private_ip(resolved_ip):
                    metadata["is_private"] = True
                    if not allow_private:
                        return False, f"Domain '{hostname}' resolves to private/internal IP ({resolved_ip}), which is not allowed", metadata
    
    # Check blacklist
    if settings.TARGET_BLACKLIST:
        for blocked in settings.TARGET_BLACKLIST:
            if blocked and (blocked in hostname_clean or any(blocked in ip for ip in metadata["resolved_ips"])):
                logger.warning(f"Blocked target attempted: {target}")
                return False, "Target is blacklisted", metadata
    
    # Check whitelist (if enabled)
    if settings.TARGET_WHITELIST:
        allowed = False
        for allowed_target in settings.TARGET_WHITELIST:
            if allowed_target and (allowed_target in hostname_clean or any(allowed_target in ip for ip in metadata["resolved_ips"])):
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
    
    # Allow localhost
    if domain.lower() == "localhost":
        return True, None
    
    # Domain pattern:
    # - Allows subdomains
    # - Allows hyphens (not at start/end of labels)
    # - Validates TLDs
    domain_pattern = r'^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?$'
    
    if not re.match(domain_pattern, domain):
        return False, "Invalid domain format"
    
    # Ensure we have at least one dot
    if '.' not in domain:
        return False, "Domain must have at least one dot"
    
    # Validate length constraints (max 253 chars for full domain)
    if len(domain) > 253:
        return False, "Domain too long (max 253 characters)"
    
    # Validate individual label lengths (max 63 chars each)
    parts = domain.split(".")
    for part in parts:
        if len(part) > 63:
            return False, f"Domain label '{part}' too long (max 63 characters)"
        if len(part) == 0:
            return False, "Empty domain label not allowed"
    
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
    Nuclei requires full URLs with scheme, preserving custom ports and paths.
    """
    hostname = metadata.get("hostname", target)
    scheme = metadata.get("scheme")
    netloc = metadata.get("netloc")
    path = metadata.get("path") or ""
    
    # If original had a scheme, use it with netloc (preserving port) and path
    if scheme:
        host_target = netloc if netloc else hostname
        return f"{scheme}://{host_target}{path}"
    
    # Otherwise default to http://
    return f"http://{hostname}"


def sanitize_scan_id(scan_id: str) -> str:
    """Sanitize scan_id to prevent injection"""
    # UUIDs should only contain alphanumeric and hyphens
    if not re.match(r'^[a-f0-9\-]{36}$', scan_id):
        raise TargetValidationError("Invalid scan_id format")
    return scan_id