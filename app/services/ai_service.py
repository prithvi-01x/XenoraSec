# app/services/ai_service.py

from typing import List, Dict, Any
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Constants for risk score calculation
NORMALIZATION_FACTOR = 15.0  # Sigmoid normalization divisor
MAX_RISK_SCORE = 10.0  # Maximum risk score
MAX_PORT_CONTRIBUTION = 1.0  # Maximum contribution from open ports


async def analyze_with_ai(vulnerabilities: List[Dict[str, Any]], open_ports: int = 0) -> float:
    """
    Risk scoring using weighted severity formula.

    Note: Despite the name, this is NOT machine learning or an LLM — it is a
    deterministic weighted-sum formula with sigmoid normalization.  The name
    is kept for API compatibility but consider renaming to `calculate_risk_score`
    in a future refactor.

    Algorithm:
        1. Sum severity-weighted scores for each vulnerability
        2. Add CVSS scores (if available) with multiplier
        3. Add open port factor
        4. Normalize to 0-10 scale via sigmoid-like function
    
    Args:
        vulnerabilities: List of vulnerability dictionaries
        open_ports: Number of open ports detected
    
    Returns:
        Risk score between 0.0 and 10.0
    """
    
    if not vulnerabilities and open_ports == 0:
        logger.info("No vulnerabilities or open ports found, risk score: 0.0")
        return 0.0
    
    weights = settings.RISK_SCORE_WEIGHTS
    score = 0.0
    cvss_scores = []
    
    # Process vulnerabilities
    for vuln in vulnerabilities:
        severity = vuln.get("severity", "unknown").lower()
        weight = weights.get(severity, weights["unknown"])
        score += weight
        
        # Handle CVSS scores
        cvss = vuln.get("cvss")
        if cvss is not None:
            # Convert string CVSS to float
            try:
                if isinstance(cvss, str):
                    cvss = float(cvss)
                if isinstance(cvss, (int, float)) and cvss > 0:
                    cvss_scores.append(float(cvss))
                    score += float(cvss) * settings.CVSS_MULTIPLIER
            except (ValueError, TypeError):
                pass
    
    # Add open port factor
    # Each open port adds a small amount to risk
    port_contribution = min(open_ports * settings.OPEN_PORT_FACTOR, MAX_PORT_CONTRIBUTION)
    score += port_contribution
    
    # Normalization logic
    # Expected max score for reference:
    # - 10 critical vulns = 50 points
    # - CVSS contribution = ~15 points (if all 10.0)
    # - Port contribution = 1 point
    # Total possible = ~66 points
    # We normalize to fit 0-10 scale
    
    # Logarithmic normalization to prevent score inflation
    # This makes lower scores more sensitive and prevents outliers
    if score > 0:
        # Use a sigmoid-like function for smooth normalization
        normalized_score = MAX_RISK_SCORE * (score / (score + NORMALIZATION_FACTOR))
    else:
        normalized_score = 0.0
    
    final_score = min(round(normalized_score, 2), MAX_RISK_SCORE)
    
    logger.info(
        f"Risk score calculated: {final_score} | "
        f"vulns={len(vulnerabilities)}, ports={open_ports}, "
        f"raw_score={round(score, 2)}, avg_cvss={round(sum(cvss_scores) / max(len(cvss_scores), 1), 2) if cvss_scores else 0}",
        extra={"risk_score": final_score}
    )
    
    return final_score


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
        severity = vuln.get("severity", "unknown").lower()
        if severity in distribution:
            distribution[severity] += 1
        else:
            distribution["unknown"] += 1
    
    return distribution