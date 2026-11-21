import pytest
from src.analyzer import FloodSenseAnalyzer


@pytest.fixture(scope="module")
def analyzer():
    return FloodSenseAnalyzer()


def test_analyzer_critical_scenario(analyzer):
    msg = "Water is rising rapidly in our village! 10 families are trapped on the terrace and need immediate boat rescue!"
    res = analyzer.analyze(msg)

    assert res["flood_detected"] is True
    assert res["severity"]["level"] == "Critical"
    assert res["severity"]["severity_rank"] == 4
    assert res["priority"]["score"] >= 80
    assert "life_threat" in res["supporting_indicators"]
    assert res["humanitarian_context"]["category"] in [
        "requests_or_urgent_needs",
        "rescue_volunteering_or_donation_effort",
    ]


def test_analyzer_high_scenario(analyzer):
    msg = "The dam has burst and water is entering houses rapidly. Highway bridge collapsed."
    res = analyzer.analyze(msg)

    assert res["flood_detected"] is True
    assert res["severity"]["level"] in ["High", "Critical"]
    assert res["priority"]["score"] >= 60
    assert "water_ingress" in res["supporting_indicators"]


def test_analyzer_moderate_scenario(analyzer):
    msg = "Flood alert issued for coastal areas. Flood warning in effect, river overflowing."
    res = analyzer.analyze(msg)

    assert res["flood_detected"] is True
    assert res["severity"]["level"] in ["Moderate", "High"]
    assert res["priority"]["score"] >= 20


def test_analyzer_low_scenario(analyzer):
    msg = "Heartfelt prayers and support for everyone dealing with flood recovery in Kerala."
    res = analyzer.analyze(msg)

    assert res["flood_detected"] is True
    assert res["severity"]["level"] == "Low"
    assert res["priority"]["score"] < 40
    assert res["humanitarian_context"]["category"] == "sympathy_and_support"


def test_analyzer_negated_scenario(analyzer):
    msg = "Situation is completely normal here, no flooding and no casualties reported."
    res = analyzer.analyze(msg)

    # Negated flood messages correctly output Non-Flood / Not Applicable
    assert res["flood_detected"] is False
    assert res["severity"]["level"] == "Not Applicable"
    assert res["priority"]["score"] == 0


def test_analyzer_non_flood_scenario(analyzer):
    msg = "Traffic accident near downtown market, police on the scene."
    res = analyzer.analyze(msg)

    assert res["flood_detected"] is False
    assert res["severity"]["level"] == "Not Applicable"
    assert res["priority"]["score"] == 0
