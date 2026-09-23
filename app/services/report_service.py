import io
import json
from datetime import datetime, UTC
from typing import Dict, List, Any, Optional
from uuid import uuid4

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    KeepTogether,
)

from app.core.config import settings
from app.core.logging import get_logger
from app.schemas.report import (
    ReportFormat,
    ReportType,
    ReportMetadata,
    ExecutiveSummary,
    CveDetail,
)
from app.services.ai_service import calculate_severity_distribution

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

    # Fallback to direct raw vulnerability counting if summary dictionary is omitted
    if not dist and nuclei.get("vulnerabilities"):
        dist = calculate_severity_distribution(nuclei.get("vulnerabilities", []))
        crit_count = dist.get("critical", 0)
        high_count = dist.get("high", 0)
        med_count = dist.get("medium", 0)
        low_count = dist.get("low", 0)
        info_count = dist.get("info", 0)

    if ports_count == 0 and nmap.get("ports"):
        ports_count = len(nmap.get("ports", []))

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


def generate_json_report(
    scan: Dict[str, Any],
    report_type: ReportType = ReportType.TECHNICAL
) -> str:
    """
    Generate structured, comprehensive JSON report export.
    """
    target = scan.get("target", "Target Host")
    scan_id = scan.get("scan_id", "unknown-scan")
    risk_score = float(scan.get("risk_score", 0.0))

    exec_summary = generate_executive_summary(scan)
    nuclei_res = scan.get("nuclei", {}) if isinstance(scan.get("nuclei"), dict) else {}
    nmap_res = scan.get("nmap", {}) if isinstance(scan.get("nmap"), dict) else {}
    cves = extract_cve_details(nuclei_res, target)

    metadata = ReportMetadata(
        report_id=f"rep-{uuid4().hex[:12]}",
        scan_id=scan_id,
        target=target,
        generated_at=datetime.now(UTC),
        report_type=report_type,
        format=ReportFormat.JSON,
        author="XenoraSec Automated Engine",
        organization=settings.REPORT_COMPANY_NAME,
        risk_score=risk_score,
        scan_profile=scan.get("scan_profile", "quick"),
    )

    report_payload: Dict[str, Any] = {
        "metadata": metadata.model_dump(mode="json"),
        "executive_summary": exec_summary.model_dump(mode="json"),
        "cve_details": [c.model_dump(mode="json") for c in cves],
        "network_perimeter": {
            "total_open_ports": nmap_res.get("total_ports", 0),
            "ports": nmap_res.get("ports", []),
            "host_info": nmap_res.get("host_info", {}),
        },
    }

    if report_type == ReportType.TECHNICAL:
        report_payload["vulnerabilities"] = nuclei_res.get("vulnerabilities", [])
        report_payload["scan_options"] = scan.get("scan_options", {})
        report_payload["scan_profile"] = scan.get("scan_profile", "quick")
        report_payload["scan_stats"] = nuclei_res.get("scan_stats", {})

    return json.dumps(report_payload, indent=2, default=str)


def generate_markdown_report(
    scan: Dict[str, Any],
    report_type: ReportType = ReportType.TECHNICAL
) -> str:
    """
    Generate professional Markdown report formatted with GitHub-flavored markdown.
    """
    target = scan.get("target", "Target Host")
    scan_id = scan.get("scan_id", "unknown-scan")
    risk_score = float(scan.get("risk_score", 0.0))
    scan_profile = scan.get("scan_profile", "quick")
    exec_summary = generate_executive_summary(scan)

    nuclei_res = scan.get("nuclei", {}) if isinstance(scan.get("nuclei"), dict) else {}
    nmap_res = scan.get("nmap", {}) if isinstance(scan.get("nmap"), dict) else {}
    cves = extract_cve_details(nuclei_res, target)
    ports = nmap_res.get("ports", [])

    report_title = "Executive Security Posture Brief" if report_type == ReportType.EXECUTIVE else "Technical Vulnerability Assessment Report"

    lines: List[str] = [
        f"# {settings.REPORT_COMPANY_NAME} — {report_title}",
        "",
        f"> **Assessment Date:** {exec_summary.scan_date.strftime('%Y-%m-%d %H:%M:%S UTC')}  ",
        f"> **Target System:** `{target}`  ",
        f"> **Scan ID:** `{scan_id}`  ",
        f"> **Scan Profile:** `{scan_profile.upper()}`  ",
        f"> **Overall Risk Score:** **{risk_score:.1f} / 10.0** — *{exec_summary.risk_category}*",
        "",
        "---",
        "",
        "## 1. Executive Summary",
        "",
        f"An automated vulnerability assessment was conducted against `{target}` utilizing XenoraSec's multi-engine security scanner. "
        f"The system concluded with an overall risk classification of **{exec_summary.risk_category}** (Score: {risk_score:.1f}/10.0).",
        "",
        "### Key Findings",
        ""
    ]

    for finding in exec_summary.key_findings:
        lines.append(f"- {finding}")
    lines.append("")

    lines.extend([
        "### Severity Distribution",
        "",
        "| Severity Level | Finding Count | Priority Status |",
        "| :--- | :--- | :--- |",
        f"| **Critical** | {exec_summary.critical_count} | {'Action Required Immediately' if exec_summary.critical_count > 0 else 'Acceptable'} |",
        f"| **High** | {exec_summary.high_count} | {'Urgent Remediation' if exec_summary.high_count > 0 else 'Acceptable'} |",
        f"| **Medium** | {exec_summary.medium_count} | {'Routine Patching' if exec_summary.medium_count > 0 else 'Acceptable'} |",
        f"| **Low** | {exec_summary.low_count} | Informational / Defense-in-Depth |",
        f"| **Info** | {exec_summary.info_count} | Perimeter Reconnaissance |",
        "",
        "### Strategic Remediation Recommendations",
        ""
    ])

    for rec in exec_summary.strategic_recommendations:
        lines.append(f"1. {rec}")
    lines.append("")

    # If Technical Report, include detailed CVE breakdowns, Ports, and Vulnerability Match details
    if report_type == ReportType.TECHNICAL:
        lines.extend([
            "---",
            "",
            "## 2. Detailed Vulnerability & CVE Findings",
            ""
        ])

        if not cves:
            lines.append("*No high or critical vulnerabilities were identified during this assessment.*")
            lines.append("")
        else:
            for idx, cve in enumerate(cves, 1):
                sev_badge = cve.severity.upper()
                cvss_str = f" (CVSS: {cve.cvss_score})" if cve.cvss_score else ""
                lines.extend([
                    f"### 2.{idx} [{sev_badge}] {cve.title}{cvss_str}",
                    "",
                    f"- **Identifier:** `{cve.cve_id}`",
                    f"- **Severity:** `{cve.severity.upper()}`",
                    f"- **Affected Location:** `{cve.affected_target}`",
                    f"- **CWE Classification:** {cve.cwe_id or 'N/A'}",
                    "",
                    "**Description:**",
                    f"{cve.description}",
                    "",
                    "**Remediation Guidance:**",
                    f"> {cve.remediation_advice}",
                    ""
                ])

                if cve.references:
                    lines.append("**Advisory References:**")
                    for ref in cve.references:
                        lines.append(f"- [{ref}]({ref})")
                    lines.append("")

        lines.extend([
            "---",
            "",
            "## 3. Network Perimeter & Open Ports",
            "",
            f"Port discovery identified **{len(ports)}** open services on `{target}`.",
            "",
            "| Port / Protocol | Service | Product / Version | Extra Info |",
            "| :--- | :--- | :--- | :--- |"
        ])

        if not ports:
            lines.append("| *None* | *No standard open ports identified* | - | - |")
        else:
            for p in ports:
                port_str = f"{p.get('port')}/{p.get('protocol', 'tcp')}"
                srv = p.get('service') or 'unknown'
                prod = f"{p.get('product', '')} {p.get('version', '')}".strip() or 'unidentified'
                extra = p.get('extrainfo') or '-'
                lines.append(f"| `{port_str}` | {srv} | {prod} | {extra} |")

        lines.extend([
            "",
            "---",
            "",
            "## 4. Assessment Methodology & Tools",
            "",
            "- **Service & Port Discovery:** Nmap Connect Engine with service fingerprinting (`-sV`).",
            "- **Vulnerability Validation:** Nuclei Template Engine with custom tag rulesets.",
            "- **Risk Analysis:** AI-assisted contextual impact and CVSS-based scoring algorithm.",
            ""
        ])

    lines.extend([
        "---",
        f"*Report generated automatically by {settings.REPORT_COMPANY_NAME}. Strictly confidential.*"
    ])

    return "\n".join(lines)


def generate_html_report(
    scan: Dict[str, Any],
    report_type: ReportType = ReportType.TECHNICAL
) -> str:
    """
    Generate an offline-capable, cyber-themed, print-optimized HTML security report.
    """
    target = scan.get("target", "Target Host")
    scan_id = scan.get("scan_id", "unknown-scan")
    risk_score = float(scan.get("risk_score", 0.0))
    scan_profile = scan.get("scan_profile", "quick")
    exec_summary = generate_executive_summary(scan)

    nuclei_res = scan.get("nuclei", {}) if isinstance(scan.get("nuclei"), dict) else {}
    nmap_res = scan.get("nmap", {}) if isinstance(scan.get("nmap"), dict) else {}
    cves = extract_cve_details(nuclei_res, target)
    ports = nmap_res.get("ports", [])

    # Color mapping for risk
    if risk_score >= 8.0 or exec_summary.critical_count > 0:
        score_color = "#ef4444"
        badge_bg = "#450a0a"
        badge_border = "#991b1b"
    elif risk_score >= 6.0 or exec_summary.high_count > 0:
        score_color = "#f97316"
        badge_bg = "#431407"
        badge_border = "#9a3412"
    elif risk_score >= 3.5 or exec_summary.medium_count > 0:
        score_color = "#eab308"
        badge_bg = "#422006"
        badge_border = "#854d0e"
    elif risk_score > 0.0 or exec_summary.low_count > 0 or len(ports) > 0:
        score_color = "#3b82f6"
        badge_bg = "#172554"
        badge_border = "#1e40af"
    else:
        score_color = "#10b981"
        badge_bg = "#064e3b"
        badge_border = "#065f46"

    # Build CVE HTML cards
    cve_cards_html = ""
    if not cves:
        cve_cards_html = """
        <div class="empty-state">
            <p>No critical, high, or medium exploitable vulnerabilities were identified during this assessment.</p>
        </div>
        """
    else:
        for idx, cve in enumerate(cves, 1):
            sev_upper = cve.severity.upper()
            sev_color = {
                "critical": "#ef4444",
                "high": "#f97316",
                "medium": "#eab308",
                "low": "#3b82f6",
                "info": "#64748b"
            }.get(cve.severity.lower(), "#64748b")

            cvss_badge = f'<span class="pill pill-cvss">CVSS {cve.cvss_score}</span>' if cve.cvss_score else ''
            cwe_badge = f'<span class="pill pill-cwe">{cve.cwe_id}</span>' if cve.cwe_id else ''

            refs_html = "".join([f'<li><a href="{r}" target="_blank" rel="noopener">{r}</a></li>' for r in cve.references])
            refs_section = f'<div class="advisory-refs"><strong>References:</strong><ul>{refs_html}</ul></div>' if refs_html else ''

            cve_cards_html += f"""
            <div class="card vuln-card" style="border-left: 4px solid {sev_color};">
                <div class="vuln-header">
                    <div class="vuln-title-wrap">
                        <span class="sev-tag" style="background: {sev_color}22; color: {sev_color}; border: 1px solid {sev_color}66;">
                            {sev_upper}
                        </span>
                        <h4 class="vuln-title">{cve.title}</h4>
                    </div>
                    <div class="pill-group">
                        <span class="pill pill-id">{cve.cve_id}</span>
                        {cvss_badge}
                        {cwe_badge}
                    </div>
                </div>
                <div class="vuln-body">
                    <p class="vuln-target"><strong>Matched Location:</strong> <code>{cve.affected_target}</code></p>
                    <p class="vuln-desc">{cve.description}</p>
                    <div class="remediation-box">
                        <strong>Remediation Advice:</strong>
                        <p>{cve.remediation_advice}</p>
                    </div>
                    {refs_section}
                </div>
            </div>
            """

    # Build ports HTML table rows
    ports_rows_html = ""
    if not ports:
        ports_rows_html = '<tr><td colspan="4" style="text-align: center; color: #64748b;">No standard open ports discovered.</td></tr>'
    else:
        for p in ports:
            port_proto = f"{p.get('port')}/{p.get('protocol', 'tcp')}"
            svc = p.get('service') or 'unknown'
            ver = f"{p.get('product', '')} {p.get('version', '')}".strip() or '-'
            extra = p.get('extrainfo') or '-'
            ports_rows_html += f"""
            <tr>
                <td><code>{port_proto}</code></td>
                <td><span class="service-tag">{svc}</span></td>
                <td>{ver}</td>
                <td class="text-muted">{extra}</td>
            </tr>
            """

    # Key findings HTML list
    findings_list_html = "".join([f"<li>{f}</li>" for f in exec_summary.key_findings])
    recs_list_html = "".join([f"<li>{r}</li>" for r in exec_summary.strategic_recommendations])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{settings.REPORT_COMPANY_NAME} - Security Report - {target}</title>
    <style>
        :root {{
            --bg: #090d16;
            --surface: #111827;
            --surface-border: #1f2937;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --primary: #3b82f6;
            --accent: #06b6d4;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background: var(--bg);
            color: var(--text-main);
            line-height: 1.6;
            padding: 32px 16px;
        }}
        .container {{
            max-width: 1040px;
            margin: 0 auto;
        }}
        header.report-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--surface-border);
            padding-bottom: 24px;
            margin-bottom: 32px;
        }}
        .brand-badge {{
            display: inline-block;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--accent);
            font-weight: 700;
            margin-bottom: 4px;
        }}
        h1.report-title {{
            font-size: 1.85rem;
            font-weight: 800;
            letter-spacing: -0.02em;
        }}
        .header-actions {{
            display: flex;
            gap: 12px;
        }}
        .btn-print {{
            background: #2563eb;
            color: #ffffff;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 0.875rem;
            cursor: pointer;
            transition: opacity 0.2s;
        }}
        .btn-print:hover {{ opacity: 0.9; }}
        
        .card {{
            background: var(--surface);
            border: 1px solid var(--surface-border);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
        }}
        .overview-grid {{
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 24px;
        }}
        @media (max-width: 768px) {{
            .overview-grid {{ grid-template-columns: 1fr; }}
        }}
        .risk-gauge-card {{
            text-align: center;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            background: {badge_bg};
            border: 1px solid {badge_border};
            border-radius: 12px;
            padding: 20px;
        }}
        .risk-score-value {{
            font-size: 3.5rem;
            font-weight: 900;
            color: {score_color};
            line-height: 1;
        }}
        .risk-score-max {{ font-size: 1.25rem; color: var(--text-muted); }}
        .risk-label {{
            font-size: 1.1rem;
            font-weight: 700;
            color: {score_color};
            margin-top: 8px;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .meta-list {{
            list-style: none;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 12px;
        }}
        .meta-item strong {{ display: block; font-size: 0.75rem; text-transform: uppercase; color: var(--text-muted); }}
        .meta-item span {{ font-size: 0.95rem; font-weight: 600; }}
        
        .counts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 12px;
            margin-top: 20px;
        }}
        .count-card {{
            background: rgba(255,255,255,0.02);
            border: 1px solid var(--surface-border);
            border-radius: 8px;
            padding: 12px;
            text-align: center;
        }}
        .count-card .val {{ font-size: 1.75rem; font-weight: 800; }}
        .count-card .lbl {{ font-size: 0.75rem; color: var(--text-muted); text-transform: uppercase; }}
        
        h2.section-heading {{
            font-size: 1.35rem;
            font-weight: 700;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
            color: #ffffff;
        }}
        ul.bullet-list {{ padding-left: 20px; margin-bottom: 16px; }}
        ul.bullet-list li {{ margin-bottom: 8px; }}
        ol.ordered-list {{ padding-left: 20px; margin-bottom: 16px; }}
        ol.ordered-list li {{ margin-bottom: 8px; }}
        
        /* Vulnerability cards */
        .vuln-card {{
            background: #111827;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 16px;
        }}
        .vuln-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            flex-wrap: wrap;
            gap: 12px;
            margin-bottom: 12px;
        }}
        .vuln-title-wrap {{
            display: flex;
            align-items: center;
            gap: 10px;
            flex-wrap: wrap;
        }}
        .sev-tag {{
            font-size: 0.75rem;
            font-weight: 800;
            padding: 2px 8px;
            border-radius: 4px;
            letter-spacing: 0.05em;
        }}
        .vuln-title {{ font-size: 1.1rem; font-weight: 700; color: #ffffff; }}
        .pill-group {{ display: flex; gap: 6px; flex-wrap: wrap; }}
        .pill {{
            font-size: 0.75rem;
            padding: 2px 8px;
            border-radius: 9999px;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.1);
            color: #e2e8f0;
        }}
        .pill-cvss {{ background: #7c2d12; color: #fed7aa; border-color: #c2410c; font-weight: 700; }}
        .vuln-body p {{ margin-bottom: 10px; font-size: 0.95rem; }}
        code {{
            background: rgba(255,255,255,0.08);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
            font-size: 0.85em;
        }}
        .remediation-box {{
            background: rgba(16, 185, 129, 0.08);
            border-left: 3px solid #10b981;
            padding: 12px;
            border-radius: 0 6px 6px 0;
            margin-top: 12px;
        }}
        .remediation-box strong {{ color: #34d399; font-size: 0.85rem; text-transform: uppercase; display: block; margin-bottom: 4px; }}
        .advisory-refs {{ margin-top: 12px; font-size: 0.85rem; }}
        .advisory-refs a {{ color: var(--primary); text-decoration: none; word-break: break-all; }}
        .advisory-refs a:hover {{ text-decoration: underline; }}

        /* Data table */
        table.data-table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 0.9rem;
        }}
        table.data-table th {{
            background: rgba(255,255,255,0.04);
            color: var(--text-muted);
            text-transform: uppercase;
            font-size: 0.75rem;
            padding: 10px 14px;
            border-bottom: 1px solid var(--surface-border);
        }}
        table.data-table td {{
            padding: 12px 14px;
            border-bottom: 1px solid rgba(255,255,255,0.04);
        }}
        .service-tag {{
            background: rgba(59, 130, 246, 0.15);
            color: #93c5fd;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 600;
        }}
        footer.report-footer {{
            text-align: center;
            font-size: 0.8rem;
            color: var(--text-muted);
            border-top: 1px solid var(--surface-border);
            padding-top: 24px;
            margin-top: 40px;
        }}

        /* Print optimization */
        @media print {{
            body {{ background: #ffffff !important; color: #111827 !important; padding: 0; }}
            .btn-print {{ display: none !important; }}
            .card {{ border: 1px solid #e5e7eb !important; background: #ffffff !important; box-shadow: none !important; color: #111827 !important; }}
            .risk-gauge-card {{ background: #f9fafb !important; border: 1px solid #d1d5db !important; }}
            .vuln-card {{ page-break-inside: avoid; border: 1px solid #e5e7eb !important; background: #f9fafb !important; color: #111827 !important; }}
            .vuln-title {{ color: #111827 !important; }}
            h1, h2, h3, h4 {{ color: #111827 !important; }}
            code {{ background: #f3f4f6 !important; color: #111827 !important; }}
            .pill {{ background: #e5e7eb !important; color: #374151 !important; border: 1px solid #d1d5db !important; }}
            table.data-table th {{ background: #f3f4f6 !important; color: #4b5563 !important; }}
            table.data-table td {{ border-bottom: 1px solid #e5e7eb !important; color: #111827 !important; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="report-header">
            <div>
                <span class="brand-badge">{settings.REPORT_COMPANY_NAME}</span>
                <h1 class="report-title">Security Assessment Report</h1>
                <p style="color: var(--text-muted); font-size: 0.875rem;">Target: <strong>{target}</strong> | Mode: <strong>{report_type.value.upper()}</strong></p>
            </div>
            <div class="header-actions">
                <button onclick="window.print()" class="btn-print">Print / Save as PDF</button>
            </div>
        </header>

        <!-- Executive Overview Card -->
        <div class="card">
            <h2 class="section-heading">Executive Security Posture</h2>
            <div class="overview-grid">
                <div>
                    <ul class="meta-list">
                        <li class="meta-item">
                            <strong>Target System</strong>
                            <span>{target}</span>
                        </li>
                        <li class="meta-item">
                            <strong>Assessment Date</strong>
                            <span>{exec_summary.scan_date.strftime('%Y-%m-%d %H:%M UTC')}</span>
                        </li>
                        <li class="meta-item">
                            <strong>Scan Profile</strong>
                            <span>{scan_profile.upper()}</span>
                        </li>
                        <li class="meta-item">
                            <strong>Assessment ID</strong>
                            <span>{scan_id[:16]}...</span>
                        </li>
                    </ul>

                    <div class="counts-grid">
                        <div class="count-card">
                            <div class="val" style="color: #ef4444;">{exec_summary.critical_count}</div>
                            <div class="lbl">Critical</div>
                        </div>
                        <div class="count-card">
                            <div class="val" style="color: #f97316;">{exec_summary.high_count}</div>
                            <div class="lbl">High</div>
                        </div>
                        <div class="count-card">
                            <div class="val" style="color: #eab308;">{exec_summary.medium_count}</div>
                            <div class="lbl">Medium</div>
                        </div>
                        <div class="count-card">
                            <div class="val" style="color: #3b82f6;">{exec_summary.open_ports_count}</div>
                            <div class="lbl">Open Ports</div>
                        </div>
                    </div>
                </div>

                <div class="risk-gauge-card">
                    <div class="risk-score-value">{risk_score:.1f}<span class="risk-score-max">/10</span></div>
                    <div class="risk-label">{exec_summary.risk_category}</div>
                </div>
            </div>
        </div>

        <!-- Key Findings & Recommendations -->
        <div class="card">
            <h2 class="section-heading">Key Findings & Strategic Recommendations</h2>
            <h3 style="font-size: 1rem; color: #94a3b8; margin-bottom: 8px;">Key Executive Observations:</h3>
            <ul class="bullet-list">
                {findings_list_html}
            </ul>

            <h3 style="font-size: 1rem; color: #94a3b8; margin-top: 16px; margin-bottom: 8px;">Remediation Priorities:</h3>
            <ol class="ordered-list">
                {recs_list_html}
            </ol>
        </div>

        <!-- Detailed Vulnerabilities -->
        <div class="card">
            <h2 class="section-heading">Vulnerabilities & CVE Breakdown ({len(cves)})</h2>
            {cve_cards_html}
        </div>

        <!-- Perimeter Exposure & Ports -->
        <div class="card">
            <h2 class="section-heading">Perimeter Port & Service Discovery ({len(ports)})</h2>
            <table class="data-table">
                <thead>
                    <tr>
                        <th>Port / Protocol</th>
                        <th>Service</th>
                        <th>Detected Product / Version</th>
                        <th>Banner / Extra</th>
                    </tr>
                </thead>
                <tbody>
                    {ports_rows_html}
                </tbody>
            </table>
        </div>

        <footer class="report-footer">
            <p>Generated by <strong>{settings.REPORT_COMPANY_NAME}</strong> automated penetration testing framework.</p>
            <p style="margin-top: 4px;">Confidential security document. Intended solely for authorized administrators.</p>
        </footer>
    </div>
</body>
</html>"""
    return html


def _escape_pdf(text: Any) -> str:
    """Escape XML special characters for ReportLab Paragraphs."""
    if text is None:
        return ""
    s = str(text)
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def generate_pdf_report(
    scan: Dict[str, Any],
    report_type: ReportType = ReportType.TECHNICAL
) -> bytes:
    """
    Generate an executive or technical PDF security report using ReportLab.
    Returns raw PDF bytes.
    """
    target = scan.get("target", "Target Host")
    scan_id = scan.get("scan_id", "unknown-scan")
    risk_score = float(scan.get("risk_score", 0.0))
    scan_profile = scan.get("scan_profile", "quick")
    exec_summary = generate_executive_summary(scan)

    nuclei_res = scan.get("nuclei", {}) if isinstance(scan.get("nuclei"), dict) else {}
    nmap_res = scan.get("nmap", {}) if isinstance(scan.get("nmap"), dict) else {}
    cves = extract_cve_details(nuclei_res, target)
    ports = nmap_res.get("ports", [])

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.white
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#94a3b8')
    )
    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=17,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=14,
        spaceAfter=6
    )
    h3_style = ParagraphStyle(
        'SectionH3',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'),
        spaceBefore=8,
        spaceAfter=4
    )
    body_style = ParagraphStyle(
        'ReportBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#1e293b')
    )
    bullet_style = ParagraphStyle(
        'ReportBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#1e293b'),
        leftIndent=14
    )
    code_style = ParagraphStyle(
        'ReportCode',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#0f172a')
    )
    footer_style = ParagraphStyle(
        'ReportFooter',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#64748b'),
        alignment=1  # Centered
    )

    story = []

    # 1. Header Banner Table
    header_data = [
        [
            Paragraph(f"<b>{_escape_pdf(settings.REPORT_COMPANY_NAME)}</b><br/><font size=14><b>Security Assessment Report</b></font>", title_style),
            Paragraph(f"<b>Target:</b> {_escape_pdf(target)}<br/>"
                      f"<b>Date:</b> {exec_summary.scan_date.strftime('%Y-%m-%d %H:%M UTC')}<br/>"
                      f"<b>Profile:</b> {_escape_pdf(scan_profile.upper())} | <b>Mode:</b> {report_type.value.upper()}", subtitle_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[320, 220])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#0f172a')),
        ('PADDING', (0, 0), (-1, -1), 12),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 14))

    # 2. Key Metrics Posture Grid
    risk_color = colors.HexColor('#10b981')
    if risk_score >= 8.0:
        risk_color = colors.HexColor('#ef4444')
    elif risk_score >= 6.0:
        risk_color = colors.HexColor('#f97316')
    elif risk_score >= 3.5:
        risk_color = colors.HexColor('#eab308')
    elif risk_score > 0.0:
        risk_color = colors.HexColor('#3b82f6')

    metric_data = [
        [
            Paragraph(f"<font color='{risk_color.hexval()}'><b>{risk_score:.1f} / 10</b></font><br/><font size=7 color='#64748b'>RISK SCORE ({exec_summary.risk_category})</font>", body_style),
            Paragraph(f"<font color='#ef4444'><b>{exec_summary.critical_count}</b></font><br/><font size=7 color='#64748b'>CRITICAL</font>", body_style),
            Paragraph(f"<font color='#f97316'><b>{exec_summary.high_count}</b></font><br/><font size=7 color='#64748b'>HIGH</font>", body_style),
            Paragraph(f"<font color='#eab308'><b>{exec_summary.medium_count}</b></font><br/><font size=7 color='#64748b'>MEDIUM</font>", body_style),
            Paragraph(f"<font color='#3b82f6'><b>{exec_summary.open_ports_count}</b></font><br/><font size=7 color='#64748b'>OPEN PORTS</font>", body_style),
        ]
    ]
    metric_table = Table(metric_data, colWidths=[110, 107, 107, 107, 107])
    metric_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(metric_table)
    story.append(Spacer(1, 10))

    # 3. Executive Observations & Recommendations
    story.append(Paragraph("Executive Observations", h2_style))
    for f in exec_summary.key_findings:
        story.append(Paragraph(f"&bull; {_escape_pdf(f)}", bullet_style))
        story.append(Spacer(1, 2))

    story.append(Spacer(1, 6))
    story.append(Paragraph("Strategic Remediation Priorities", h3_style))
    for idx, r in enumerate(exec_summary.strategic_recommendations, 1):
        story.append(Paragraph(f"<b>{idx}.</b> {_escape_pdf(r)}", bullet_style))
        story.append(Spacer(1, 2))

    # 4. Detailed Vulnerabilities (Technical report or findings exist)
    if report_type == ReportType.TECHNICAL or cves:
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cbd5e1'), spaceBefore=8, spaceAfter=8))
        story.append(Paragraph(f"Vulnerabilities &amp; CVE Details ({len(cves)})", h2_style))

        if not cves:
            story.append(Paragraph("<i>No critical, high, or medium exploitable vulnerabilities were identified during this assessment.</i>", body_style))
        else:
            for cve in cves:
                sev_color = {
                    "critical": "#ef4444",
                    "high": "#f97316",
                    "medium": "#eab308",
                    "low": "#3b82f6",
                    "info": "#64748b"
                }.get(cve.severity.lower(), "#64748b")

                vuln_elements = [
                    [
                        Paragraph(f"<font color='{sev_color}'><b>[{cve.severity.upper()}]</b></font> <b>{_escape_pdf(cve.title)}</b> ({_escape_pdf(cve.cve_id)})", body_style),
                        Paragraph(f"<b>CVSS:</b> {cve.cvss_score if cve.cvss_score else 'N/A'}", body_style)
                    ],
                    [
                        Paragraph(f"<b>Target:</b> {_escape_pdf(cve.affected_target)}", code_style),
                        Paragraph(f"<b>CWE:</b> {_escape_pdf(cve.cwe_id if cve.cwe_id else 'N/A')}", body_style)
                    ],
                    [
                        Paragraph(f"<b>Description:</b> {_escape_pdf(cve.description)}", body_style),
                        Paragraph("", body_style)
                    ],
                    [
                        Paragraph(f"<b>Remediation:</b> <font color='#065f46'>{_escape_pdf(cve.remediation_advice)}</font>", body_style),
                        Paragraph("", body_style)
                    ]
                ]
                vuln_table = Table(vuln_elements, colWidths=[430, 110])
                vuln_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
                    ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor('#cbd5e1')),
                    ('LINEBEFORE', (0, 0), (0, -1), 3, colors.HexColor(sev_color)),
                    ('SPAN', (0, 2), (1, 2)),
                    ('SPAN', (0, 3), (1, 3)),
                    ('PADDING', (0, 0), (-1, -1), 5),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                story.append(KeepTogether([vuln_table, Spacer(1, 6)]))

    # 5. Open Ports & Services
    if report_type == ReportType.TECHNICAL:
        story.append(Spacer(1, 8))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#cbd5e1'), spaceBefore=8, spaceAfter=8))
        story.append(Paragraph(f"Discovered Ports &amp; Perimeter Services ({len(ports)})", h2_style))

        if not ports:
            story.append(Paragraph("<i>No standard open ports discovered during perimeter scan.</i>", body_style))
        else:
            port_table_data = [
                [
                    Paragraph("<b>Port / Protocol</b>", body_style),
                    Paragraph("<b>Service</b>", body_style),
                    Paragraph("<b>Product / Version</b>", body_style),
                    Paragraph("<b>Extra Info</b>", body_style)
                ]
            ]
            for p in ports:
                port_proto = f"{p.get('port')}/{p.get('protocol', 'tcp')}"
                svc = p.get('service') or 'unknown'
                prod = f"{p.get('product', '')} {p.get('version', '')}".strip() or '-'
                extra = p.get('extrainfo') or '-'
                port_table_data.append([
                    Paragraph(f"<code>{_escape_pdf(port_proto)}</code>", code_style),
                    Paragraph(_escape_pdf(svc), body_style),
                    Paragraph(_escape_pdf(prod), body_style),
                    Paragraph(_escape_pdf(extra), body_style)
                ])

            port_table = Table(port_table_data, colWidths=[110, 110, 180, 140])
            port_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
                ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                ('PADDING', (0, 0), (-1, -1), 4.5),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            story.append(port_table)

    # 6. Confidentiality Footer
    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e2e8f0'), spaceBefore=8, spaceAfter=8))
    story.append(Paragraph(
        f"Generated automatically by <b>{_escape_pdf(settings.REPORT_COMPANY_NAME)}</b> automated penetration testing platform.<br/>"
        "CONFIDENTIAL &amp; PROPRIETARY &mdash; FOR AUTHORIZED RECIPIENTS ONLY",
        footer_style
    ))

    doc.build(story)
    return buf.getvalue()
