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


def test_analyzer_stuck_in_floodwaters_regression(analyzer):
    """Regression test for Example 1: Three people stuck in the floodwaters."""
    msg = "Three people stuck in the floodwaters."
    res = analyzer.analyze(msg)

    assert res["flood_detected"] is True
    assert res["severity"]["level"] == "Critical"
    assert res["severity"]["severity_rank"] == 4
    assert res["priority"]["tier"] == "P1 - Critical Priority"
    assert res["priority"]["score"] >= 80
    assert "life_threat" in res["supporting_indicators"]


def test_analyzer_children_stuck_rising_water_regression(analyzer):
    """Regression test for Example 2: Two children are stuck in the house and the flood water level is rising."""
    msg = "Two children are stuck in the house and the flood water level is rising."
    res = analyzer.analyze(msg)

    assert res["flood_detected"] is True
    assert res["severity"]["level"] == "Critical"
    assert res["severity"]["severity_rank"] == 4
    assert res["priority"]["tier"] == "P1 - Critical Priority"
    assert res["priority"]["score"] >= 90
    assert "life_threat" in res["supporting_indicators"]
    assert "water_dynamics" in res["supporting_indicators"]


def test_analyzer_entrapment_variations(analyzer):
    """Verify equivalent natural-language expressions for entrapment in flood emergencies."""
    # Variation 1: Elderly resident trapped on upper floor with ingress
    res1 = analyzer.analyze("Elderly resident trapped on the second floor as floodwater enters the building.")
    assert res1["severity"]["level"] == "Critical"
    assert res1["priority"]["tier"] == "P1 - Critical Priority"
    assert "life_threat" in res1["supporting_indicators"]

    # Variation 2: Family stuck inside vehicle with rising water
    res2 = analyzer.analyze("Family is stuck inside their car surrounded by rising flood water.")
    assert res2["severity"]["level"] == "Critical"
    assert res2["priority"]["tier"] == "P1 - Critical Priority"
    assert "life_threat" in res2["supporting_indicators"]
    assert "water_dynamics" in res2["supporting_indicators"]

    # Variation 3: Marooned on roof with boat rescue
    res3 = analyzer.analyze("Four people marooned on roof needing urgent boat rescue.")
    assert res3["severity"]["level"] == "Critical"
    assert res3["priority"]["tier"] == "P1 - Critical Priority"
    assert "life_threat" in res3["supporting_indicators"]


def test_analyzer_negative_and_context_filtering_safety(analyzer):
    """Safety checks: verify non-emergency, routine, negated, and hypothetical messages are not over-triaged."""
    # 1. Non-flood children playing
    res1 = analyzer.analyze("Children playing in the water park.")
    assert res1["flood_detected"] is False
    assert res1["severity"]["level"] == "Not Applicable"
    assert res1["priority"]["tier"] == "P0 - Non-Emergency / Routine"

    # 2. Non-flood vehicle stuck in traffic
    res2 = analyzer.analyze("Traffic is stuck on Highway 10 due to construction work.")
    assert res2["flood_detected"] is False
    assert res2["severity"]["level"] == "Not Applicable"

    # 3. Flood traffic delay (not life threat)
    res3 = analyzer.analyze("Delivery truck got stuck in traffic during the flood.")
    assert res3["flood_detected"] is True
    assert res3["severity"]["level"] in ["Moderate", "High"]
    assert res3["priority"]["tier"] != "P1 - Critical Priority"

    # 4. Explicit negation of entrapment
    res4 = analyzer.analyze("No people are stuck in the floodwaters, all were safely rescued.")
    assert res4["severity"]["level"] == "Low"
    assert res4["priority"]["score"] <= 20

    # 5. Historical retrospective entrapment
    res5 = analyzer.analyze("In 2018, three people were stuck in the floodwaters.")
    assert res5["severity"]["level"] == "Low"
    assert res5["priority"]["score"] <= 20

    # 6. Hypothetical question
    res6 = analyzer.analyze("What if children get stuck in the house during the flood?")
    assert res6["severity"]["level"] == "Low"
    assert res6["priority"]["score"] <= 20


def test_analyzer_context_sensitive_entrapment_scenarios(analyzer):
    """Context-sensitive tests covering nuanced edge cases:
    1. People trapped in a flooded house with no rescue available -> Critical P1
    2. People stuck in a house during a flood warning, but with no actual flooding -> Low P4
    3. People trapped in floodwater after rescuers have already arrived -> Low P4
    4. Negated and historical entrapment statements -> Low / Not Applicable
    """
    # 1. Trapped in flooded house with no rescue available (Active Critical P1)
    res1 = analyzer.analyze("People are trapped in a flooded house with no rescue available.")
    assert res1["flood_detected"] is True
    assert res1["severity"]["level"] == "Critical"
    assert res1["priority"]["tier"] == "P1 - Critical Priority"
    assert "life_threat" in res1["supporting_indicators"]

    # 2. Stuck during warning, but with NO actual flooding (Negation detected -> Low P4)
    res2 = analyzer.analyze("People are stuck in the house during a flood warning, but with no actual flooding.")
    assert res2["flood_detected"] is True
    assert res2["severity"]["level"] == "Low"
    assert res2["priority"]["tier"] == "P4 - Low Priority"
    assert res2["priority"]["score"] <= 20
    assert len(res2["supporting_indicators"]) == 0

    # 3. Rescuers have already arrived (Mitigated / Under control -> Low P4)
    res3 = analyzer.analyze("People were trapped in floodwater, but rescue teams have already arrived and everyone is safe.")
    assert res3["flood_detected"] is True
    assert res3["severity"]["level"] == "Low"
    assert res3["priority"]["tier"] == "P4 - Low Priority"
    assert res3["priority"]["score"] <= 20

    # 4a. Negated entrapment statement
    res4a = analyzer.analyze("The situation is safe, no one is trapped in the house and the water has receded.")
    assert res4a["severity"]["level"] in ["Low", "Not Applicable"]
    assert res4a["priority"]["score"] <= 20

    # 4b. Historical entrapment statement
    res4b = analyzer.analyze("During the 2018 flood, residents were trapped in their houses as waters rose.")
    assert res4b["flood_detected"] is True
    assert res4b["severity"]["level"] == "Low"
    assert res4b["priority"]["tier"] == "P4 - Low Priority"
    assert res4b["priority"]["score"] <= 20


