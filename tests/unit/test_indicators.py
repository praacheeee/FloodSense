import pytest
from src.severity.indicators import extract_indicators


def test_extract_life_threat_active():
    msg = "Water is rising rapidly and 4 families are trapped on the terrace! Need immediate rescue!"
    res = extract_indicators(msg)

    assert "life_threat" in res["active_indicators"]
    assert "water_dynamics" in res["active_indicators"]
    assert res["indicator_count"] == 2
    assert not res["context_modifiers"]["negated"]
    assert not res["context_modifiers"]["hypothetical"]
    assert not res["context_modifiers"]["historical"]


def test_extract_negation():
    msg = "No casualties and no flooding inside the houses here, situation is under control."
    res = extract_indicators(msg)

    assert res["context_modifiers"]["negated"] is True
    # Indicators should be discounted rather than active
    assert len(res["active_indicators"]) == 0
    assert len(res["discounted_indicators"]) > 0


def test_extract_hypothetical():
    msg = "If the dam burst occurs, water could flood the lower village."
    res = extract_indicators(msg)

    assert res["context_modifiers"]["hypothetical"] is True
    assert len(res["active_indicators"]) == 0
    assert "water_dynamics" in res["discounted_indicators"]


def test_extract_historical():
    msg = "Remembering the devastating flood in 2018 when bridges collapsed and many died."
    res = extract_indicators(msg)

    assert res["context_modifiers"]["historical"] is True
    assert len(res["active_indicators"]) == 0
    assert "casualty" in res["discounted_indicators"]


def test_anti_double_counting():
    msg = "People are trapped, families are trapped, residents are trapped!"
    res = extract_indicators(msg)

    # All belong to life_threat family; canonical indicator count should be 1
    assert res["indicator_count"] == 1
    assert "life_threat" in res["active_indicators"]


def test_empty_input():
    res = extract_indicators("   ")
    assert res["indicator_count"] == 0
    assert len(res["active_indicators"]) == 0
