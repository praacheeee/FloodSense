"""
Provisional Rule-Grounded Severity Classifier for FloodSense.

Classifies emergency messages into primary severity levels:
- Critical: Acute life threat (trapped, stranded, drowning, active casualties needing urgent rescue)
- High: Severe hazard & displacement (water entering homes, cut-off routes, structural damage)
- Moderate: Advisory, localized waterlogging, property impact, relief logistics
- Low: Informational, emotional support, general updates, or negated hazards

Note:
This rule-based decision engine represents a provisional baseline designed for
transparent situation triage. As noted in docs/severity_annotation_guidelines.md,
this model must be further evaluated against independently annotated multi-annotator
severity ground truth. HumAID category predictions serve strictly as supporting
humanitarian context and are NOT treated as 1:1 severity mappings.
"""

from typing import Any, Dict, List, Optional
from src.severity.indicators import extract_indicators


class SeverityClassifier:
    """
    Classifies flood message severity based on grounded physical indicators
    corroborated by supporting humanitarian communication context.
    """

    SEVERITY_LEVELS = ["Low", "Moderate", "High", "Critical"]

    def __init__(self):
        pass

    def classify_severity(
        self,
        text: str,
        is_flood_related: bool = True,
        humaid_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Classify the emergency severity of a message.

        Parameters:
        - text: The original or preprocessed message text.
        - is_flood_related: Binary flood detection status.
        - humaid_context: Supporting context from the trained HumAID model
          (e.g., predicted_category, confidence, class_probabilities).
        """
        if not is_flood_related:
            return {
                "severity": "Not Applicable",
                "severity_rank": 0,
                "confidence_assessment": "non_flood_suppressed",
                "reasoning": "Message determined to be not flood-related.",
                "supporting_indicators": [],
                "provisional_baseline": True,
            }

        indicator_data = extract_indicators(text)
        active_inds = indicator_data["active_indicators"]
        modifiers = indicator_data["context_modifiers"]
        active_evidence = indicator_data["active_evidence"]

        # Extract supporting HumAID signal if available
        pred_cat = humaid_context.get("predicted_category") if humaid_context else None
        cat_conf = humaid_context.get("confidence") if humaid_context else 0.0

        factors: List[str] = []

        # 1. Check for Context Downgrades (Negation / Pure Historical)
        if modifiers["negated"]:
            return {
                "severity": "Low",
                "severity_rank": 1,
                "confidence_assessment": "explicit_negation_detected",
                "reasoning": "Explicit negation detected (hazard, casualties, or damage denied/under control).",
                "supporting_indicators": [],
                "discounted_indicators": indicator_data["discounted_indicators"],
                "humanitarian_context": pred_cat,
                "provisional_baseline": True,
            }

        if modifiers["historical"]:
            return {
                "severity": "Low",
                "severity_rank": 1,
                "confidence_assessment": "historical_retrospective_detected",
                "reasoning": "Message identified as a retrospective or historical event description.",
                "supporting_indicators": [],
                "discounted_indicators": indicator_data["discounted_indicators"],
                "humanitarian_context": pred_cat,
                "provisional_baseline": True,
            }

        if modifiers["hypothetical"]:
            return {
                "severity": "Low",
                "severity_rank": 1,
                "confidence_assessment": "hypothetical_conditional_detected",
                "reasoning": "Message describes a hypothetical or conditional flood scenario rather than an active emergency.",
                "supporting_indicators": [],
                "discounted_indicators": indicator_data["discounted_indicators"],
                "humanitarian_context": pred_cat,
                "provisional_baseline": True,
            }

        # 2. Critical Evaluation: Direct Life Threat
        # Active life threat indicators (trapped, drowning, stranded, stuck in water or structure)
        # OR active casualties with urgent rescue needs
        # OR acute entrapment combination (residential water ingress + rising water with occupants)
        if "life_threat" in active_inds:
            factors.append("Active life threat detected (trapped/stranded/stuck individuals or immediate rescue plea)")
            if "water_dynamics" in active_inds or "water_ingress" in active_inds:
                factors.append("Acute life threat compounded by rising or encroaching floodwaters")
            if pred_cat in ["requests_or_urgent_needs", "injured_or_dead_people"]:
                factors.append(f"Corroborated by humanitarian signal: {pred_cat} (conf: {cat_conf:.2f})")

            return {
                "severity": "Critical",
                "severity_rank": 4,
                "confidence_assessment": "grounded_life_threat",
                "reasoning": "; ".join(factors),
                "supporting_indicators": list(active_inds.keys()),
                "evidence_snippets": active_evidence,
                "humanitarian_context": pred_cat,
                "provisional_baseline": True,
            }

        # Multi-indicator acute risk combination: residential water ingress + rising water dynamics with occupants
        if ("water_ingress" in active_inds and "water_dynamics" in active_inds) and any(
            w in text.lower() for w in ["people", "family", "families", "children", "child", "someone", "residents", "elderly", "we", "occupants"]
        ):
            factors.append("Severe entrapment risk: residential water ingress compounded by rising floodwaters with occupants inside")
            return {
                "severity": "Critical",
                "severity_rank": 4,
                "confidence_assessment": "grounded_residential_entrapment_risk",
                "reasoning": "; ".join(factors),
                "supporting_indicators": list(active_inds.keys()),
                "evidence_snippets": active_evidence,
                "humanitarian_context": pred_cat,
                "provisional_baseline": True,
            }

        if "casualty" in active_inds and ("water_dynamics" in active_inds or pred_cat == "requests_or_urgent_needs"):
            factors.append("Casualties reported in active flood zone with immediate response needs")
            return {
                "severity": "Critical",
                "severity_rank": 4,
                "confidence_assessment": "grounded_casualties_in_hazard",
                "reasoning": "; ".join(factors),
                "supporting_indicators": list(active_inds.keys()),
                "evidence_snippets": active_evidence,
                "humanitarian_context": pred_cat,
                "provisional_baseline": True,
            }

        # 3. High Evaluation: Major Hazard, Structural Ingress, or Evacuation
        # Requires actual water ingress into homes/buildings, or community displacement/evacuation,
        # or major critical infrastructure failure.
        if "water_ingress" in active_inds or "infrastructure_impact" in active_inds or "evacuation_displacement" in active_inds:
            if "water_ingress" in active_inds:
                factors.append("Active water ingress into residences/buildings or structural submergence observed")
            if "infrastructure_impact" in active_inds:
                factors.append("Critical infrastructure, transit routes, or utility failure detected")
            if "evacuation_displacement" in active_inds:
                factors.append("Active evacuation orders or community displacement reported")

            return {
                "severity": "High",
                "severity_rank": 3,
                "confidence_assessment": "grounded_structural_hazard",
                "reasoning": "; ".join(factors),
                "supporting_indicators": list(active_inds.keys()),
                "evidence_snippets": active_evidence,
                "humanitarian_context": pred_cat,
                "provisional_baseline": True,
            }

        # 4. Moderate Evaluation: Warnings, Alerts, River Dynamics without Structural Ingress, Logistics
        if "water_dynamics" in active_inds or pred_cat in ["caution_and_advice", "rescue_volunteering_or_donation_effort", "infrastructure_and_utility_damage"]:
            if "water_dynamics" in active_inds:
                factors.append("Flood warning, weather advisory, or rising/overflowing river conditions observed")
            if pred_cat in ["caution_and_advice", "rescue_volunteering_or_donation_effort", "infrastructure_and_utility_damage"]:
                factors.append(f"Humanitarian advisory, logistical effort, or utility report: {pred_cat}")

            return {
                "severity": "Moderate",
                "severity_rank": 2,
                "confidence_assessment": "humanitarian_advisory_or_relief",
                "reasoning": "; ".join(factors),
                "supporting_indicators": list(active_inds.keys()),
                "evidence_snippets": active_evidence,
                "humanitarian_context": pred_cat,
                "provisional_baseline": True,
            }

        # 5. Low: General context, sympathy, news, or unclassified
        factors.append("General discussion, emotional support, or informational update without active danger indicators")
        return {
            "severity": "Low",
            "severity_rank": 1,
            "confidence_assessment": "general_or_informational",
            "reasoning": "; ".join(factors),
            "supporting_indicators": list(active_inds.keys()),
            "evidence_snippets": active_evidence,
            "humanitarian_context": pred_cat,
            "provisional_baseline": True,
        }
