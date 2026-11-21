"""
Inference wrapper for the trained HumAID humanitarian category classifier.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import joblib

from src.preprocessing.preprocess import normalize_text, preprocess_message


class HumAIDClassifier:
    """
    Inference interface for classifying emergency messages into
    HumAID humanitarian categories.

    Note: This classifier outputs humanitarian communication categories
    (e.g., rescue efforts, urgent needs, infrastructure damage) and does
    NOT assign severity levels or priority ratings.
    """

    def __init__(self, pipeline_path: Optional[Path] = None):
        if pipeline_path is None:
            pipeline_path = Path(__file__).resolve().parents[2] / "models" / "humaid_classifier_pipeline.joblib"

        self.pipeline_path = Path(pipeline_path)
        if not self.pipeline_path.exists():
            raise FileNotFoundError(f"Model pipeline artifact not found at {self.pipeline_path}")

        self.pipeline = joblib.load(self.pipeline_path)
        self.classes_ = list(self.pipeline.classes_)

    def predict(self, text: str) -> Dict[str, Any]:
        """
        Classify a single raw emergency message.
        Returns the predicted category and calibrated class probabilities.
        """
        preprocessed = preprocess_message(text)
        cleaned_text = preprocessed["cleaned_text"]

        # Predict category
        pred_label = str(self.pipeline.predict([cleaned_text])[0])

        # Calibrated probability distribution
        if hasattr(self.pipeline, "predict_proba"):
            probs = self.pipeline.predict_proba([cleaned_text])[0]
            confidence_distribution = {
                str(cls_name): round(float(prob), 4)
                for cls_name, prob in zip(self.classes_, probs)
            }
            top_confidence = round(float(max(probs)), 4)
        else:
            confidence_distribution = None
            top_confidence = None

        return {
            "original_text": preprocessed["original_text"],
            "cleaned_text": cleaned_text,
            "predicted_category": pred_label,
            "confidence": top_confidence,
            "class_probabilities": confidence_distribution,
            "model_type": "tfidf_calibrated_linearsvc",
            "scope": "HumAID humanitarian categories (non-severity)",
        }

    def predict_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Classify a batch of emergency messages."""
        return [self.predict(t) for t in texts]
