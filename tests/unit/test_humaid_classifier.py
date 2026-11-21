import pytest
from src.classification.humaid_classifier import HumAIDClassifier


@pytest.fixture
def classifier():
    return HumAIDClassifier()


def test_humaid_classifier_prediction(classifier):
    message = "Water level rising rapidly, several people are trapped in their houses and need boat rescue!"
    result = classifier.predict(message)

    assert "predicted_category" in result
    assert "confidence" in result
    assert "class_probabilities" in result
    assert result["confidence"] is not None
    assert 0.0 <= result["confidence"] <= 1.0
    assert result["predicted_category"] in classifier.classes_
    assert len(result["class_probabilities"]) == 10

    # Ensure probabilities sum close to 1
    total_prob = sum(result["class_probabilities"].values())
    assert abs(total_prob - 1.0) < 0.05


def test_humaid_classifier_batch(classifier):
    messages = [
        "Praying for everyone affected by the Kerala flood",
        "Bridge collapsed due to flood waters near national highway",
    ]
    results = classifier.predict_batch(messages)
    assert len(results) == 2
    assert results[0]["predicted_category"] == "sympathy_and_support"
    assert results[1]["predicted_category"] == "infrastructure_and_utility_damage"
