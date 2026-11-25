import re
from typing import Dict, List

FLOOD_PATTERNS = {
    "Flood event": [
        r"\bflood(?:s|ed|ing)?\b",
        r"\bflash flood(?:s)?\b",
        r"\bfloodwaters?\b",
        r"\bflood waters?\b",
    ],
    "Rising water": [
        r"\b(?:flood\s*)?waters?\s+(?:(?:is|are)\s+)?rising\b",
        r"\brising\s+(?:flood\s*)?waters?\b",
        r"\b(?:flood\s*)?waters?\s+levels?\s+(?:(?:is|are)\s+)?rising\b",
        r"\b(?:flood\s*)?waters?\s+levels?\s+(?:(?:is|are)\s+)?increasing\b",
    ],
    "Water entering areas": [
        r"\b(?:flood\s*)?waters?\s+(?:is\s+)?entering (?:the )?(?:houses?|homes?|buildings?|villages?)\b",
        r"\b(?:flood\s*)?waters?\s+inside (?:the )?(?:houses?|homes?|buildings?)\b",
        r"\bsubmerged\b",
        r"\binundated\b",
        r"\bunder water\b",
    ],
    "River or dam overflow": [
        r"\briver overflow(?:ing)?\b",
        r"\briver has overflowed\b",
        r"\bdam (?:has )?burst\b",
        r"\bdam failure\b",
    ],
    "Flood emergency": [
        r"\bflood warning\b",
        r"\bflood alert\b",
        r"\bflood evacuation\b",
        r"\bflood rescue\b",
        r"\b(?:rescue\s+boat|boat\s+rescue)\b",
    ],
}

NEGATION_PATTERNS = [
    r"\bno flooding\b",
    r"\bno flood(?:ing)?\b",
    r"\bnot flooded\b",
    r"\bnot flooding\b",
    r"\bwithout flooding\b",
]


def classify_flood_message(text: str) -> Dict:
    if not isinstance(text, str):
        raise TypeError("Input must be a string.")

    cleaned_text = text.lower().strip()

    if not cleaned_text:
        raise ValueError("Message cannot be empty.")

    for pattern in NEGATION_PATTERNS:
        if re.search(pattern, cleaned_text):
            return {
                "flood_related": False,
                "indicators": [],
                "assessment_type": "rule_based_baseline",
                "reason": "Explicit flood negation detected."
            }

    matched_indicators: List[str] = []

    for category, patterns in FLOOD_PATTERNS.items():
        if any(re.search(pattern, cleaned_text) for pattern in patterns):
            matched_indicators.append(category)

    return {
        "flood_related": bool(matched_indicators),
        "indicators": matched_indicators,
        "assessment_type": "rule_based_baseline",
        "reason": (
            "Flood-related expressions detected."
            if matched_indicators
            else "No recognized flood-related expressions detected."
        )
    }
