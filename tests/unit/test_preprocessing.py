
from src.preprocessing.preprocess import (
    normalize_text,
    preprocess_message
)


def test_normalize_text():
    result = normalize_text("WATER IS RISING!!!")
    assert result == "water is rising!!!"


def test_preserve_emergency_words():
    result = normalize_text(
        "People are TRAPPED and need urgent RESCUE!"
    )

    assert "trapped" in result
    assert "urgent" in result
    assert "rescue" in result


def test_preprocess_message():
    result = preprocess_message(
        "Flood water is rising near our house!"
    )

    assert result["original_text"]
    assert "flood water" in result["cleaned_text"]


def test_empty_message():
    try:
        preprocess_message("   ")
        assert False, "Expected ValueError"
    except ValueError:
        pass


if __name__ == "__main__":
    test_normalize_text()
    test_preserve_emergency_words()
    test_preprocess_message()
    test_empty_message()

    print("All preprocessing tests passed!")
