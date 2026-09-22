# tests/test_ai_service.py

import pytest
from unittest.mock import patch, AsyncMock
from app.services.ai_service import (
    calculate_heuristic_risk_score,
    analyze_with_ai,
    analyze_with_groq_llm,
    calculate_severity_distribution
)
from app.core.config import settings


def test_heuristic_zero_findings():
    score = calculate_heuristic_risk_score([], 0)
    assert score == 0.0


def test_heuristic_saturation_mathematics():
    # Test half-saturation point where raw_score = 15.0
    # 3 critical vulns (weight 5.0 each) = 15.0 raw score
    # Score = 10.0 * (15 / (15 + 15)) = 5.0
    vulns = [
        {"severity": "critical"},
        {"severity": "critical"},
        {"severity": "critical"}
    ]
    score = calculate_heuristic_risk_score(vulns, open_ports=0)
    assert score == 5.0


def test_heuristic_diminishing_returns():
    # As raw findings grow to huge numbers, score approaches 10.0 but never exceeds it
    vulns = [{"severity": "critical", "cvss": 10.0} for _ in range(500)]
    score = calculate_heuristic_risk_score(vulns, open_ports=100)
    assert 9.5 <= score <= 10.0


@pytest.mark.asyncio
async def test_groq_fallback_when_api_key_unset():
    settings.GROQ_API_KEY = None
    vulns = [{"severity": "high"}]  # weight 3.0
    # raw score = 3.0. Score = 10 * 3 / 18 = 1.67
    score = await analyze_with_ai(vulns, open_ports=0)
    assert score == 1.67


@pytest.mark.asyncio
async def test_groq_llm_success_and_parsing():
    from unittest.mock import MagicMock
    settings.GROQ_API_KEY = "gsk-mock-key"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {"message": {"content": '{"risk_score": 8.75, "reasoning": "Exposed RCE vulnerability"}'}}
        ]
    }

    with patch("httpx.AsyncClient.post", AsyncMock(return_value=mock_response)):
        score = await analyze_with_groq_llm([{"name": "RCE", "severity": "critical"}], open_ports=2)
        assert score == 8.75


@pytest.mark.asyncio
async def test_groq_llm_failure_falls_back_to_heuristic():
    settings.GROQ_API_KEY = "gsk-mock-key"
    with patch("httpx.AsyncClient.post", side_effect=Exception("Network error")):
        vulns = [{"severity": "medium"}]
        score = await analyze_with_ai(vulns, open_ports=0)
        # Fallback to heuristic: raw score = 2.0 -> 10 * 2 / 17 = 1.18
        assert score == 1.18
