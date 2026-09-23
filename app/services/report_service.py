# app/services/report_service.py

import json
from datetime import datetime, UTC
from typing import Dict, List, Any, Optional
from uuid import uuid4

from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.report import (
    ReportFormat,
    ReportType,
    ReportMetadata,
    ExecutiveSummary,
    CveDetail,
    RemediationAdvice,
)

logger = get_logger(__name__)


def extract_cve_details(nuclei_result: Dict[str, Any], target: str) -> List[CveDetail]:
    """
    Extract and structure CVE details from Nuclei findings.
    """
    vulns = nuclei_result.get("vulnerabilities", []) if isinstance(nuclei_result, dict) else []
    cve_map: Dict[str, CveDetail] = {}

    for v in vulns:
        cve_id = v.get("cve")
        template_id = v.get("template_id") or "unknown-template"
        name = v.get("name") or template_id
        severity = v.get("severity", "info").lower()
        cvss = v.get("cvss")
        cwe = v.get("cwe")
        matched = v.get("matched_at") or target
        desc = v.get("description") or f"Detected via Nuclei template {template_id}"
        refs = v.get("references") or []

        # Key by CVE ID if available, else by template_id
        key = cve_id or template_id
        if key not in cve_map:
            remediation = _generate_cve_remediation(key, name, severity)
            cve_map[key] = CveDetail(
                cve_id=key,
                title=name,
                severity=severity,
                cvss_score=cvss,
                cwe_id=cwe,
                affected_target=matched,
                description=desc,
                remediation_advice=remediation,
                references=refs[:5] if isinstance(refs, list) else []
            )

    return list(cve_map.values())


def _generate_cve_remediation(cve_or_id: str, name: str, severity: str) -> str:
    """Generate contextual remediation advice based on finding metadata."""
    name_lower = name.lower()
    if "rce" in name_lower or "command execution" in name_lower:
        return "CRITICAL: Immediately isolate the affected endpoint from external ingress. Patch the vulnerable underlying software package or implement strict input sanitization/WAF virtual patching."
    elif "sqli" in name_lower or "sql injection" in name_lower:
        return "HIGH: Enforce parameterized queries (prepared statements) or ORM mapping across all database access layers. Never concatenate unsanitized user parameters directly into SQL queries."
    elif "auth" in name_lower or "bypass" in name_lower or "unauthenticated" in name_lower:
        return "HIGH: Audit access control matrices and ensure token verification is enforced on every backend route. Invalidate exposed administrative credentials."
    elif "cve-" in cve_or_id.lower():
        return f"Apply vendor security updates addressing {cve_or_id}. If direct patching requires scheduling maintenance, apply compensatory firewall/WAF filtering rules."
    elif severity == "critical":
        return "Emergency patch required: review official vendor advisories and disable the exposed service or component until a verified security hotfix is deployed."
    elif severity == "high":
        return "Prioritize remediation in current sprint. Validate software dependencies and apply updated patches."
    elif severity == "medium":
        return "Schedule remediation in routine maintenance window. Verify configuration against security benchmarks (CIS / OWASP)."
    else:
        return "Review exposure against organizational security policy and remove unnecessary information banners or exposed internal endpoints."


def generate_executive_summary(scan: Dict[str, Any]) -> ExecutiveSummary:
    """
    Synthesize an executive-level security posture summary suitable for board or leadership review.
    """
    target = scan.get("target", "Target Host")
    created_at = scan.get("created_at") or datetime.now(UTC)
    if isinstance(created_at, str):
        try:
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        except Exception:
            created_at = datetime.now(UTC)

    risk_score = float(scan.get("risk_score", 0.0))
    summary = scan.get("summary", {}) if isinstance(scan.get("summary"), dict) else {}
    nmap = scan.get("nmap", {}) if isinstance(scan.get("nmap"), dict) else {}
    nuclei = scan.get("nuclei", {}) if isinstance(scan.get("nuclei"), dict) else {}

    crit_count = summary.get("critical_count", 0)
    high_count = summary.get("high_count", 0)
    dist = summary.get("severity_distribution", {}) or {}
    med_count = dist.get("medium", 0)
    low_count = dist.get("low", 0)
    info_count = dist.get("info", 0)
    ports_count = nmap.get("total_ports", 0)

    # Risk categorization
    if risk_score >= 8.0 or crit_count > 0:
        risk_category = "Critical Risk"
    elif risk_score >= 6.0 or high_count > 0:
        risk_category = "Elevated / High Risk"
    elif risk_score >= 3.5 or med_count > 0:
        risk_category = "Moderate Risk"
    elif ports_count > 0 or low_count > 0:
        risk_category = "Low Risk / Exposed Perimeter"
    else:
        risk_category = "Minimal Risk"

    # Key findings
    key_findings = []
    if crit_count > 0:
        key_findings.append(f"{crit_count} Critical-severity vulnerabilities identified requiring immediate mitigation.")
    if high_count > 0:
        key_findings.append(f"{high_count} High-severity security issues present significant breach exposure.")
    if ports_count > 0:
        key_findings.append(f"{ports_count} publicly accessible network ports detected across the external perimeter.")
    if not key_findings:
        key_findings.append("No critical or high-risk exploitable vulnerabilities identified during this assessment.")

    # Strategic recommendations
    recommendations = []
    if crit_count > 0 or high_count > 0:
        recommendations.append("Mobilize incident response/engineering to deploy patches for critical and high findings within 24-48 hours.")
    if ports_count > 5:
        recommendations.append("Enforce least-privilege network egress and ingress rules; close non-essential open ports via firewall.")
    recommendations.append("Implement automated continuous surface monitoring to catch regressions before deployment.")
    recommendations.append("Conduct follow-up verification scans post-remediation to confirm complete issue resolution.")

    return ExecutiveSummary(
        target=target,
        scan_date=created_at,
        overall_risk=risk_score,
        risk_category=risk_category,
        critical_count=crit_count,
        high_count=high_count,
        medium_count=med_count,
        low_count=low_count,
        info_count=info_count,
        open_ports_count=ports_count,
        key_findings=key_findings,
        strategic_recommendations=recommendations,
    )
