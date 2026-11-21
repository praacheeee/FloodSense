import pytest
from src.priority.priority_scorer import PriorityScorer


@pytest.fixture
def scorer():
    return PriorityScorer()


def test_priority_critical_life_threat(scorer):
    sev_result = {"severity": "Critical"}
    indicator_data = {
        "active_indicators": {
            "life_threat": ["trapped on roof"],
            "water_dynamics": ["water is rising rapidly"],
        }
    }
    humaid_context = {"predicted_category": "requests_or_urgent_needs", "confidence": 0.85}

    res = scorer.compute_priority(sev_result, indicator_data, humaid_context)

    # 60 (base) + 25 (life threat) + 10 (water dynamics) + 5 (urgent need) = 100
    assert res["priority_score"] == 100
    assert res["priority_tier"] == "P1 - Critical Priority"
    assert len(res["score_breakdown"]) == 4
    assert res["disclaimer"] is not None


def test_priority_capping_at_100(scorer):
    sev_result = {"severity": "Critical"}
    indicator_data = {
        "active_indicators": {
            "life_threat": ["trapped"],
            "casualty": ["fatalities reported"],
            "water_ingress": ["submerged"],
            "infrastructure_impact": ["bridge collapsed"],
        }
    }
    # 60 + 25 + 20 + 15 + 10 = 130 -> clamped to 100
    res = scorer.compute_priority(sev_result, indicator_data)
    assert res["priority_score"] == 100
    assert res["priority_tier"] == "P1 - Critical Priority"


def test_priority_anti_double_counting(scorer):
    sev_result = {"severity": "High"}
    # Multiple life_threat spans should only be counted once
    indicator_data = {
        "active_indicators": {
            "life_threat": ["trapped", "marooned", "stranded on roof"],
        }
    }
    res = scorer.compute_priority(sev_result, indicator_data)
    # 40 (base) + 25 (life_threat once) = 65
    assert res["priority_score"] == 65
    assert res["priority_tier"] == "P2 - High Priority"
    assert len([b for b in res["score_breakdown"] if b["type"] == "indicator_bonus"]) == 1


def test_priority_non_flood(scorer):
    sev_result = {"severity": "Not Applicable"}
    res = scorer.compute_priority(sev_result, {})
    assert res["priority_score"] == 0
    assert res["priority_tier"] == "P0 - Non-Emergency / Routine"


def test_priority_tier_congruence_regression(scorer):
    """Regression test ensuring severity level and priority tier never conflict."""
    pairs = [
        ("Critical", "P1 - Critical Priority"),
        ("High", "P2 - High Priority"),
        ("Moderate", "P3 - Moderate Priority"),
        ("Low", "P4 - Low Priority"),
        ("Not Applicable", "P0 - Non-Emergency / Routine"),
    ]
    for sev, expected_tier in pairs:
        res = scorer.compute_priority({"severity": sev}, {})
        assert res["priority_tier"] == expected_tier, (
            f"Mismatch: Severity {sev} produced {res['priority_tier']}, expected {expected_tier}"
        )
