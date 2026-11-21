"""
Explainable Priority Scorer for FloodSense.

Computes a deterministic, explainable priority score (0 - 100) based on
validated severity indicators and supporting humanitarian context.

Disclaimers & Safety:
- This is a provisional baseline situational awareness metric.
- It is NOT an official emergency services dispatch standard.
- Anti-double-counting: Points are awarded at most once per indicator family.
"""

from typing import Any, Dict, List, Optional


class PriorityScorer:
    """
    Computes situational priority score with a transparent line-item audit trail.
    """

    SEVERITY_BASE_SCORES = {
        "Critical": 60,
        "High": 40,
        "Moderate": 25,
        "Low": 5,
        "Not Applicable": 0,
    }

    INDICATOR_BONUSES = {
        "life_threat": (25, "Active life threat (trapped/stranded individuals)"),
        "casualty": (20, "Casualties, injuries, or missing persons reported"),
        "water_ingress": (15, "Active water ingress into residences or structural submergence"),
        "water_dynamics": (10, "Rapid water level rise or overflowing conditions"),
        "infrastructure_impact": (10, "Critical infrastructure, bridge, or utility damage"),
        "evacuation_displacement": (10, "Active evacuation in progress or displaced community"),
    }

    DISCLAIMER = (
        "Provisional baseline score for automated situational awareness; "
        "not an official emergency dispatch mandate or human triage substitute."
    )

    def __init__(self):
        pass

    def compute_priority(
        self,
        severity_result: Dict[str, Any],
        indicator_data: Optional[Dict[str, Any]] = None,
        humaid_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Compute an explainable priority score.

        Parameters:
        - severity_result: Output from SeverityClassifier.
        - indicator_data: Output from extract_indicators.
        - humaid_context: Supporting context from HumAIDClassifier.
        """
        severity = severity_result.get("severity", "Low")
        base_score = self.SEVERITY_BASE_SCORES.get(severity, 0)

        breakdown: List[Dict[str, Any]] = []

        if base_score > 0:
            breakdown.append({
                "factor": f"{severity} severity baseline",
                "points": base_score,
                "type": "severity_base",
            })

        current_score = base_score

        # Indicator bonus points (Strictly deduplicated per family)
        active_inds = (
            indicator_data.get("active_indicators", {})
            if indicator_data
            else {}
        )

        for family, (bonus_pts, description) in self.INDICATOR_BONUSES.items():
            if family in active_inds:
                current_score += bonus_pts
                breakdown.append({
                    "factor": description,
                    "points": bonus_pts,
                    "type": "indicator_bonus",
                    "evidence": active_inds[family][:3],  # Up to 3 evidence snippets
                })

        # Contextual corroboration bonus
        if humaid_context:
            cat = humaid_context.get("predicted_category")
            conf = humaid_context.get("confidence", 0.0)
            if cat == "requests_or_urgent_needs" and conf >= 0.60:
                humaid_pts = 5
                current_score += humaid_pts
                breakdown.append({
                    "factor": f"Corroborated by high-confidence urgent need signal ({conf:.2f})",
                    "points": humaid_pts,
                    "type": "context_corroboration",
                })

        # Cap score between 0 and 100
        final_score = max(0, min(100, current_score))

        # Assign Priority Tier (Strictly congruent with Severity Level)
        if severity == "Critical" or final_score >= 70:
            tier = "P1 - Critical Priority"
        elif severity == "High" or final_score >= 50:
            tier = "P2 - High Priority"
        elif severity == "Moderate" or final_score >= 25:
            tier = "P3 - Moderate Priority"
        elif final_score > 0:
            tier = "P4 - Low Priority"
        else:
            tier = "P0 - Non-Emergency / Routine"

        return {
            "priority_score": final_score,
            "priority_tier": tier,
            "score_breakdown": breakdown,
            "severity_level": severity,
            "disclaimer": self.DISCLAIMER,
            "provisional_baseline": True,
        }
