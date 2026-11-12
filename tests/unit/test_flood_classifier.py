from src.classification.flood_classifier import classify_flood_message


def test_direct_flood_message():
    result = classify_flood_message("Severe flooding in our village.")
    assert result["flood_related"] is True


def test_rising_water_message():
    result = classify_flood_message(
        "Water is rising rapidly near our homes."
    )
    assert result["flood_related"] is True


def test_dam_failure_message():
    result = classify_flood_message(
        "The dam has burst and water is entering the village."
    )
    assert result["flood_related"] is True


def test_unrelated_message():
    result = classify_flood_message(
        "There is a road accident near the market."
    )
    assert result["flood_related"] is False


def test_explicit_negation():
    result = classify_flood_message(
        "There is no flooding in our area."
    )
    assert result["flood_related"] is False


def test_empty_message():
    try:
        classify_flood_message("")
        assert False, "Expected ValueError"
    except ValueError:
        pass


if __name__ == "__main__":
    test_direct_flood_message()
    test_rising_water_message()
    test_dam_failure_message()
    test_unrelated_message()
    test_explicit_negation()
    test_empty_message()

    print("All flood classification tests passed!")
