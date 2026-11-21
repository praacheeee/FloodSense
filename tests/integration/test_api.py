import pytest
from fastapi import HTTPException
from backend.app.main import health_check, system_info, analyze_message, AnalyzeRequest


def test_api_health_endpoint():
    res = health_check()
    assert res["status"] == "online"
    assert "analyzer_ready" in res


def test_api_info_endpoint():
    res = system_info()
    assert res["system"] == "FloodSense"
    assert "humanitarian_classifier" in res["models"]
    assert "disclaimer" in res


def test_api_analyze_critical_endpoint():
    req = AnalyzeRequest(
        message="Water is rising rapidly, families are trapped inside houses and need urgent boat rescue!"
    )
    res = analyze_message(req)
    assert res["flood_detected"] is True
    assert res["severity"]["level"] == "Critical"
    assert res["priority"]["score"] >= 80
    assert len(res["priority"]["score_breakdown"]) > 0


def test_api_analyze_non_flood_endpoint():
    req = AnalyzeRequest(
        message="There is a power outage in the office downtown."
    )
    res = analyze_message(req)
    assert res["flood_detected"] is False
    assert res["severity"]["level"] == "Not Applicable"
    assert res["priority"]["score"] == 0


def test_api_analyze_empty_validation():
    try:
        AnalyzeRequest(message="")
        assert False, "Expected ValueError on empty message"
    except Exception:
        pass
