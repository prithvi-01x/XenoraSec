# app/services/profile_service.py

from typing import Dict, List, Any, Optional
from app.schemas.scan import ScanProfile, ScanOptions


# Available scan profiles
SCAN_PROFILES: Dict[str, Dict[str, Any]] = {
    ScanProfile.QUICK.value: {
        "id": ScanProfile.QUICK.value,
        "name": "Quick Recon",
        "description": "Fast discovery of standard web and core services with essential CVE and misconfiguration checks.",
        "icon": "zap",
        "estimated_duration": "1 - 3 mins",
        "recommended_for": "Initial surface discovery, fast sanity checks, continuous CI checks",
        "defaults": {
            "port_range": "1-1000",
            "nmap_timing": "T4",
            "nuclei_tags": ["cve", "misconfig", "exposure"],
            "rate_limit": 100,
            "concurrency": 10,
        }
    },
    ScanProfile.FULL.value: {
        "id": ScanProfile.FULL.value,
        "name": "Full Web Audit",
        "description": "Deep security audit across web interfaces with extensive vulnerability signatures (RCE, SQLi, Auth Bypass, CVEs).",
        "icon": "shield-alert",
        "estimated_duration": "5 - 10 mins",
        "recommended_for": "Thorough pre-deployment audits, bug bounty targets, production security reviews",
        "defaults": {
            "port_range": "80,443,8000,8080,8443,8888,9000,9443",
            "nmap_timing": "T4",
            "nuclei_tags": [
                "cve",
                "rce",
                "sqli",
                "xss",
                "auth-bypass",
                "misconfig",
                "exposure",
                "default-login",
                "takeover"
            ],
            "rate_limit": 50,
            "concurrency": 8,
        }
    },
    ScanProfile.NETWORK.value: {
        "id": ScanProfile.NETWORK.value,
        "name": "Network Discovery",
        "description": "Broad port scanning and network perimeter mapping across thousands of common ports.",
        "icon": "network",
        "estimated_duration": "3 - 8 mins",
        "recommended_for": "Perimeter exposure mapping, unlisted service detection, firewall audits",
        "defaults": {
            "port_range": "1-10000",
            "nmap_timing": "T4",
            "nuclei_tags": ["network", "exposure", "default-login", "misconfig"],
            "rate_limit": 80,
            "concurrency": 10,
        }
    },
    ScanProfile.CUSTOM.value: {
        "id": ScanProfile.CUSTOM.value,
        "name": "Custom Profile",
        "description": "Fully customizable scanner parameters, selective Nuclei tags, custom port ranges, and timing controls.",
        "icon": "sliders",
        "estimated_duration": "Configurable",
        "recommended_for": "Targeted exploit verification, custom scope testing, stealth or aggressive scanning",
        "defaults": {
            "port_range": "1-1000",
            "nmap_timing": "T4",
            "nuclei_tags": ["cve", "misconfig", "exposure"],
            "rate_limit": 100,
            "concurrency": 10,
        }
    }
}


# Nuclei template tag catalog
NUCLEI_TEMPLATE_TAGS: List[Dict[str, Any]] = [
    {
        "id": "cve",
        "name": "Known CVEs",
        "category": "vulnerabilities",
        "description": "Known Common Vulnerabilities and Exposures across popular platforms and frameworks.",
        "severity": "critical",
        "recommended": True
    },
    {
        "id": "rce",
        "name": "Remote Code Execution",
        "category": "critical",
        "description": "High-impact templates testing for command execution and arbitrary code execution.",
        "severity": "critical",
        "recommended": True
    },
    {
        "id": "auth-bypass",
        "name": "Authentication Bypass",
        "category": "access",
        "description": "Flaws allowing unauthenticated access to protected administrative and API functions.",
        "severity": "high",
        "recommended": True
    },
    {
        "id": "misconfig",
        "name": "Misconfigurations",
        "category": "configuration",
        "description": "Insecure server headers, open debug endpoints, default configurations, and weak permissions.",
        "severity": "medium",
        "recommended": True
    },
    {
        "id": "exposure",
        "name": "Information Disclosure",
        "category": "data-leak",
        "description": "Exposed environment files, git repositories, secret keys, logs, and sensitive data.",
        "severity": "medium",
        "recommended": True
    },
    {
        "id": "default-login",
        "name": "Default Credentials",
        "category": "access",
        "description": "Default passwords and administrative credentials on panels, databases, and routers.",
        "severity": "high",
        "recommended": False
    },
    {
        "id": "sqli",
        "name": "SQL Injection",
        "category": "injection",
        "description": "SQL injection flaws in parameters, headers, and endpoints.",
        "severity": "high",
        "recommended": False
    },
    {
        "id": "xss",
        "name": "Cross-Site Scripting",
        "category": "injection",
        "description": "Reflected and stored XSS vectors across web interfaces.",
        "severity": "medium",
        "recommended": False
    },
    {
        "id": "takeover",
        "name": "Subdomain Takeover",
        "category": "cloud",
        "description": "Dangling DNS records and misconfigured third-party service mappings.",
        "severity": "high",
        "recommended": False
    },
    {
        "id": "network",
        "name": "Network Services",
        "category": "infrastructure",
        "description": "Network protocol tests including SSH, FTP, Telnet, Redis, and Mongo probes.",
        "severity": "medium",
        "recommended": False
    },
    {
        "id": "tech",
        "name": "Technology Detection",
        "category": "recon",
        "description": "Fingerprinting web frameworks, servers, CMS systems, and libraries.",
        "severity": "info",
        "recommended": False
    },
]


def get_available_profiles() -> List[Dict[str, Any]]:
    """Return all available scan profiles with their configuration defaults."""
    return list(SCAN_PROFILES.values())


def get_available_tags() -> List[Dict[str, Any]]:
    """Return catalog of available Nuclei template tags."""
    return NUCLEI_TEMPLATE_TAGS


def resolve_scan_options(
    profile_name: Optional[str] = None,
    custom_options: Optional[ScanOptions] = None
) -> Dict[str, Any]:
    """
    Resolve effective scan options by combining profile defaults with user overrides.
    
    Args:
        profile_name: Requested profile ('quick', 'full', 'network', 'custom')
        custom_options: Optional user-supplied ScanOptions
        
    Returns:
        Dictionary of resolved options (port_range, nmap_timing, nuclei_tags, etc.)
    """
    profile_key = (profile_name or ScanProfile.QUICK.value).lower()
    if profile_key not in SCAN_PROFILES:
        profile_key = ScanProfile.QUICK.value

    profile_defaults = SCAN_PROFILES[profile_key]["defaults"].copy()

    resolved = {
        "profile": profile_key,
        "port_range": profile_defaults["port_range"],
        "nmap_timing": profile_defaults["nmap_timing"],
        "nuclei_tags": list(profile_defaults.get("nuclei_tags", [])),
        "nuclei_templates": None,
        "rate_limit": profile_defaults.get("rate_limit", 100),
        "concurrency": profile_defaults.get("concurrency", 10),
        "allow_private": False,
        "allow_localhost": True,
        "severity_filter": None,
    }

    # If custom options were provided, apply overrides
    if custom_options:
        if custom_options.port_range:
            resolved["port_range"] = custom_options.port_range
        if custom_options.nmap_timing:
            resolved["nmap_timing"] = custom_options.nmap_timing
        if custom_options.nuclei_tags is not None:
            resolved["nuclei_tags"] = custom_options.nuclei_tags
        if custom_options.nuclei_templates is not None:
            resolved["nuclei_templates"] = custom_options.nuclei_templates
        if custom_options.rate_limit:
            resolved["rate_limit"] = custom_options.rate_limit
        if custom_options.concurrency:
            resolved["concurrency"] = custom_options.concurrency
        if custom_options.severity_filter is not None:
            resolved["severity_filter"] = custom_options.severity_filter
        resolved["allow_private"] = custom_options.allow_private
        resolved["allow_localhost"] = custom_options.allow_localhost

    return resolved
