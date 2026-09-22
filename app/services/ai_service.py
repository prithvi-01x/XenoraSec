# app/services/ai_service.py

import json
import httpx
from typing import List, Dict, Any, Optional
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Constants for risk score calculation
# The heuristic scoring engine employs a Michaelis-Menten / Hill-type saturation model:
#   Risk Score = V_max * (S / (S + K_m))
# where:
#   V_max = 10.0  (asymptotic ceiling of the risk score)
#   K_m   = 15.0  (half-saturation constant, raw score required to reach 5.0)
#   S     = accumulated raw score from severity weights, CVSS contributions, and open ports.
NORMALIZATION_FACTOR = 15.0  # K_m: half-saturation constant
MAX_RISK_SCORE = 10.0        # V_max: maximum reachable score
MAX_PORT_CONTRIBUTION = 1.0  # Maximum contribution from open ports


def calculate_heuristic_risk_score(vulnerabilities: List[Dict[str, Any]], open_ports: int = 0) -> float:
    """
    Deterministic risk scoring using the Michaelis-Menten / Hill saturation model.

    Mathematical Formulation:
        S = sum(Weight(v)) + sum(CVSS(v) * CVSS_MULTIPLIER) + min(open_ports * OPEN_PORT_FACTOR, MAX_PORT_CONTRIBUTION)
        Risk Score = V_max * (S / (S + K_m))

    Properties of the Saturation Function:
        1. Monotonicity: d(Score)/dS > 0 for all S >= 0 (risk strictly increases as findings accumulate).
        2. Strict Boundedness: As S -> inf, Score -> 10.0 asymptotically; Score never exceeds 10.0.
        3. Diminishing Marginal Risk: d^2(Score)/dS^2 < 0 for all S > 0, ensuring that the first critical
           finding introduces significant risk while subsequent findings follow an intuitive saturation curve.
        4. Half-Saturation: When raw score S equals K_m (15.0), the resulting risk score is exactly 5.0/10.0.

    Args:
        vulnerabilities: List of vulnerability dictionaries from Nuclei
        open_ports: Number of open network ports from Nmap

    Returns:
        float: Risk score bounded between 0.0 and 10.0
    """
    if not vulnerabilities and open_ports == 0:
        logger.info("No vulnerabilities or open ports found, risk score: 0.0")
        return 0.0

    weights = settings.RISK_SCORE_WEIGHTS
    raw_score = 0.0
    cvss_scores = []

    # 1. Accumulate vulnerability severity weights and CVSS contributions
    for vuln in vulnerabilities:
        severity = str(vuln.get("severity", "unknown")).lower()
        weight = weights.get(severity, weights.get("unknown", 0.5))
        raw_score += weight

        cvss = vuln.get("cvss")
        if cvss is not None:
            try:
                cvss_val = float(cvss)
                if cvss_val > 0:
                    cvss_scores.append(cvss_val)
                    raw_score += cvss_val * settings.CVSS_MULTIPLIER
            except (ValueError, TypeError):
                pass

    # 2. Add open ports exposure factor (capped at MAX_PORT_CONTRIBUTION)
    port_contribution = min(open_ports * settings.OPEN_PORT_FACTOR, MAX_PORT_CONTRIBUTION)
    raw_score += port_contribution

    # 3. Apply Michaelis-Menten saturation normalization
    if raw_score > 0:
        normalized_score = MAX_RISK_SCORE * (raw_score / (raw_score + NORMALIZATION_FACTOR))
    else:
        normalized_score = 0.0

    final_score = min(round(normalized_score, 2), MAX_RISK_SCORE)

    logger.info(
        f"Heuristic risk score computed: {final_score} | "
        f"vulns={len(vulnerabilities)}, ports={open_ports}, raw_score={round(raw_score, 2)}",
        extra={"risk_score": final_score}
    )

    return final_score


async def analyze_with_groq_llm(
    vulnerabilities: List[Dict[str, Any]], 
    open_ports: int = 0
) -> Optional[float]:
    """
    Optional LLM-assisted risk analysis via Groq Cloud API.
    
    Sends a structured summary of findings to Groq LLM (e.g. Llama 3.3 70B)
    to perform contextual holistic assessment of threat exposure.
    Falls back cleanly to None on any error or missing API key.
    """
    if not settings.GROQ_API_KEY:
        return None

    api_key = settings.GROQ_API_KEY.strip()
    if not api_key:
        return None

    # Prepare compact summary payload for the prompt
    findings_summary = []
    for v in vulnerabilities[:30]:  # Cap at top 30 findings to stay within token limits
        findings_summary.append({
            "name": v.get("name", "Unknown"),
            "severity": v.get("severity", "unknown"),
            "cvss": v.get("cvss"),
            "cve": v.get("cve"),
            "type": v.get("type")
        })

    system_prompt = (
        "You are an expert cybersecurity risk scoring engine. "
        "Analyze the discovered security findings and open ports. "
        "Return a valid JSON object with the key 'risk_score' containing a single float "
        "between 0.0 (no risk) and 10.0 (critical imminent compromise), and a brief 'reasoning' summary."
    )

    user_prompt = (
        f"Target Findings Summary:\n"
        f"- Total Open Ports: {open_ports}\n"
        f"- Total Vulnerabilities: {len(vulnerabilities)}\n"
        f"- Sample Findings: {json.dumps(findings_summary)}\n\n"
        f"Respond in JSON format: {{\"risk_score\": <float between 0.0 and 10.0>, \"reasoning\": \"<brief>\"}}"
    )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }

    try:
        async with httpx.AsyncClient(timeout=settings.GROQ_TIMEOUT) as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload
            )

            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                score = float(parsed.get("risk_score", 0.0))
                bounded_score = max(0.0, min(round(score, 2), 10.0))
                logger.info(
                    f"Groq LLM risk score: {bounded_score} (model: {settings.GROQ_MODEL})",
                    extra={"risk_score": bounded_score, "ai_provider": "groq"}
                )
                return bounded_score
            else:
                logger.warning(f"Groq API returned HTTP {response.status_code}: {response.text[:200]}")
    except Exception as e:
        logger.debug(f"Groq LLM risk analysis request failed: {e}")

    return None


async def analyze_with_ai(vulnerabilities: List[Dict[str, Any]], open_ports: int = 0) -> float:
    """
    Combined AI risk assessment orchestrator.
    Attempts Groq LLM evaluation when configured; seamlessly falls back
    to the deterministic Michaelis-Menten saturation model.

    Args:
        vulnerabilities: List of vulnerability dictionaries
        open_ports: Number of open ports detected

    Returns:
        Risk score between 0.0 and 10.0
    """
    if not vulnerabilities and open_ports == 0:
        return 0.0

    # 1. Try real LLM evaluation if Groq API key is configured
    if settings.GROQ_API_KEY:
        groq_score = await analyze_with_groq_llm(vulnerabilities, open_ports)
        if groq_score is not None:
            return groq_score

    # 2. Deterministic mathematical saturation fallback
    return calculate_heuristic_risk_score(vulnerabilities, open_ports)


async def analyze_vulnerability_report(
    nmap_result: Dict[str, Any],
    nuclei_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Analyze combined scan results and generate risk assessment.
    
    Args:
        nmap_result: Nmap scan output
        nuclei_result: Nuclei scan output
    
    Returns:
        Dictionary with risk_score and summary
    """
    vulnerabilities = nuclei_result.get("vulnerabilities", [])
    open_ports = nmap_result.get("total_ports", 0)
    severity_dist = nuclei_result.get("severity_distribution", {})
    
    # Calculate risk score
    risk_score = await analyze_with_ai(vulnerabilities, open_ports)
    
    # Build summary
    summary = {
        "total_vulnerabilities": len(vulnerabilities),
        "open_ports": open_ports,
        "severity_distribution": severity_dist,
        "critical_count": severity_dist.get("critical", 0),
        "high_count": severity_dist.get("high", 0),
        "medium_count": severity_dist.get("medium", 0),
        "low_count": severity_dist.get("low", 0),
        "info_count": severity_dist.get("info", 0),
    }
    
    # Add risk level classification
    if risk_score >= 8.0:
        risk_level = "critical"
    elif risk_score >= 6.0:
        risk_level = "high"
    elif risk_score >= 4.0:
        risk_level = "medium"
    elif risk_score >= 2.0:
        risk_level = "low"
    else:
        risk_level = "minimal"
    
    summary["risk_level"] = risk_level
    
    return {
        "risk_score": risk_score,
        "summary": summary
    }


def calculate_severity_distribution(vulnerabilities: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Calculate distribution of vulnerabilities by severity.
    
    Args:
        vulnerabilities: List of vulnerability dictionaries
    
    Returns:
        Dictionary mapping severity -> count
    """
    distribution = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "info": 0,
        "unknown": 0
    }
    
    for vuln in vulnerabilities:
        severity = str(vuln.get("severity", "unknown")).lower()
        if severity in distribution:
            distribution[severity] += 1
        else:
            distribution["unknown"] += 1
    
    return distribution