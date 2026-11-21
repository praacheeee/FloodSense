"""
Unified FloodSense Analysis Orchestrator.

Orchestrates the 5-stage FloodSense pipeline:
1. Preprocessing & Normalization
2. Binary Flood Relevance Detection
3. Supporting Humanitarian Category Classification (Trained LinearSVC)
4. Grounded Context-Aware Indicator Extraction
5. Primary Severity Classification & Explainable Priority Scoring
"""

from typing import Any, Dict, List, Optional
from src.classification.flood_classifier import classify_flood_message
from src.classification.humaid_classifier import HumAIDClassifier
from src.preprocessing.preprocess import preprocess_message
from src.priority.priority_scorer import PriorityScorer
from src.severity.indicators import extract_indicators
from src.severity.severity_classifier import SeverityClassifier


class FloodSenseAnalyzer:
    """
    End-to-end analyzer for incoming flood emergency messages.
    """

    def __init__(self, humaid_classifier: Optional[HumAIDClassifier] = None):
        if humaid_classifier is None:
            self.humaid_classifier = HumAIDClassifier()
        else:
            self.humaid_classifier = humaid_classifier

        self.severity_classifier = SeverityClassifier()
        self.priority_scorer = PriorityScorer()

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Execute full 5-stage analysis on a single emergency message.
        """
        # Stage 1: Validation and text normalization
        prep = preprocess_message(text)
        original_text = prep["original_text"]
        cleaned_text = prep["cleaned_text"]

        # Stage 2: Flood relevance check
        flood_check = classify_flood_message(original_text)
        is_flood = flood_check["flood_related"]

        if not is_flood:
            return {
                "message": original_text,
                "flood_detected": False,
                "flood_detection_reason": flood_check["reason"],
                "severity": {
                    "level": "Not Applicable",
                    "severity_rank": 0,
                    "reasoning": "Message does not contain recognized flood indicators.",
                },
                "priority": {
                    "score": 0,
                    "tier": "P0 - Non-Emergency / Routine",
                    "score_breakdown": [],
                },
                "humanitarian_category": None,
                "supporting_indicators": [],
                "disclaimer": self.priority_scorer.DISCLAIMER,
            }

        # Stage 3: Supporting Humanitarian Context (Trained HumAID Model)
        humaid_res = self.humaid_classifier.predict(cleaned_text)

        # Stage 4: Context-Aware Indicator Extraction
        indicators = extract_indicators(cleaned_text)

        # Stage 5: Primary Severity & Priority
        severity_res = self.severity_classifier.classify_severity(
            cleaned_text,
            is_flood_related=True,
            humaid_context=humaid_res,
        )

        priority_res = self.priority_scorer.compute_priority(
            severity_res,
            indicator_data=indicators,
            humaid_context=humaid_res,
        )

        return {
            "message": original_text,
            "flood_detected": True,
            "flood_detection_reason": flood_check["reason"],
            "severity": {
                "level": severity_res["severity"],
                "severity_rank": severity_res["severity_rank"],
                "reasoning": severity_res["reasoning"],
                "confidence_assessment": severity_res["confidence_assessment"],
                "evidence_snippets": severity_res.get("evidence_snippets", []),
            },
            "priority": {
                "score": priority_res["priority_score"],
                "tier": priority_res["priority_tier"],
                "score_breakdown": priority_res["score_breakdown"],
            },
            "humanitarian_context": {
                "category": humaid_res["predicted_category"],
                "confidence": humaid_res["confidence"],
                "note": "Supporting communication classification only; not a severity score.",
            },
            "supporting_indicators": list(indicators["active_indicators"].keys()),
            "context_modifiers": indicators["context_modifiers"],
            "disclaimer": priority_res["disclaimer"],
        }
