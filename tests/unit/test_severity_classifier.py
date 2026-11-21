import pytest
from src.severity.severity_classifier import SeverityClassifier


@pytest.fixture
def classifier():
    return SeverityClassifier()


def test_classify_critical_life_threat(classifier):
    msg = "Water is rising rapidly, our family is trapped on the roof and we need immediate rescue!"
    res = classifier.classify_severity(msg, is_flood_related=True)
    assert res["severity"] == "Critical"
    assert res["severity_rank"] == 4
    assert "life_threat" in res["supporting_indicators"]


def test_classify_high_water_ingress(classifier):
    msg = "Water is entering the house and ground floor is completely submerged."
    res = classifier.classify_severity(msg, is_flood_related=True)
    assert res["severity"] == "High"
    assert res["severity_rank"] == 3
    assert "water_ingress" in res["supporting_indicators"]


def test_classify_moderate_warning_regression(classifier):
    """Regression test: flood warnings and river overflows without house ingress must be Moderate."""
    msg = "Flood alert issued for coastal zones. Flood warning in effect, river overflowing."
    res = classifier.classify_severity(
        msg,
        is_flood_related=True,
        humaid_context={"predicted_category": "caution_and_advice", "confidence": 0.80}
    )
    assert res["severity"] == "Moderate"
    assert res["severity_rank"] == 2


def test_classify_moderate_advisory(classifier):
    msg = "Heavy rainfall expected tomorrow, caution advised near river banks."
    res = classifier.classify_severity(
        msg,
        is_flood_related=True,
        humaid_context={"predicted_category": "caution_and_advice", "confidence": 0.85}
    )
    assert res["severity"] == "Moderate"
    assert res["severity_rank"] == 2


def test_classify_low_sympathy(classifier):
    msg = "Praying for everyone in Kerala flood affected areas, stay strong."
    res = classifier.classify_severity(
        msg,
        is_flood_related=True,
        humaid_context={"predicted_category": "sympathy_and_support", "confidence": 0.90}
    )
    assert res["severity"] == "Low"
    assert res["severity_rank"] == 1


def test_classify_negation_override(classifier):
    # Even if "casualties" appears, negation "no casualties" should keep it Low
    msg = "The water has receded, no casualties and no one is trapped."
    res = classifier.classify_severity(msg, is_flood_related=True)
    assert res["severity"] == "Low"
    assert res["severity_rank"] == 1


def test_classify_non_flood(classifier):
    msg = "Road accident reported on the highway."
    res = classifier.classify_severity(msg, is_flood_related=False)
    assert res["severity"] == "Not Applicable"
    assert res["severity_rank"] == 0
