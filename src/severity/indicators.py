"""
Context-Aware Indicator Extraction Engine for Flood Emergencies.

Extracts grounded physical and situational evidence from text:
- Life threat (trapped, stranded, drowning, vulnerable persons)
- Casualty (injuries, deaths, missing persons)
- Water dynamics (rapidly rising water, water entering homes, dam overflow)
- Infrastructure impact (bridges, roads, electrical grid, hospitals)
- Evacuation & displacement (evacuation orders, relief camps)

Applies rigorous contextual filtering:
- Negation detection ("no casualties", "not trapped")
- Hypothetical / conditional detection ("if the dam breaks")
- Historical / retrospective detection ("in 2018 floods")
- Speculation / unverified rumors ("unconfirmed rumors")
"""

import re
from typing import Any, Dict, List, Set


# Regex patterns for core indicator families
INDICATOR_PATTERNS = {
    "life_threat": [
        # People or vulnerable groups trapped, stranded, stuck, or marooned
        r"\b(?:(?:\d+|one|two|three|four|five|six|several|many|some|few)\s+)?(?:people|families|family|residents?|children|child|kids?|we|they|someone|parents?|persons?|citizens?)\s+(?:(?:are|is)\s+)?(?:trapped|stranded|stuck|marooned)\b",
        # Entrapment directly in or by floodwaters/water
        r"\b(?:trapped|stranded|stuck|marooned)\s+(?:in|by|amid|under)\s+(?:the\s+)?(?:floodwaters?|flood\s+waters?|rising\s+waters?|flood|floods|water)\b",
        # Entrapment in structures, buildings, roofs, or elevated locations
        r"\b(?:trapped|stranded|stuck|marooned)\s+(?:on|in|inside)\s+(?:the\s+)?(?:roof|terrace|tree|road|island|building|houses?|homes?|attics?|second\s+floor|rooms?|vehicles?|cars?)\b",
        r"\b(?:trapped|stranded|stuck|marooned)\s+inside\b",
        # Inability to escape or evacuate
        r"\b(?:people|families|residents|children|we|someone)\s+(?:are\s+)?(?:unable|cannot|can't)\s+(?:to\s+)?(?:leave|escape|evacuate|get\s+out)\b",
        r"\bmarooned\b",
        r"\b(?:drowning|swept\s+away)\b",
        # Urgent rescue pleas
        r"\bimmediate\s+rescue\s+(?:needed|required|plea)\b",
        r"\bneed\s+(?:urgent\s+)?(?:boat|helicopter|airlift)\s+rescue\b",
        # Vulnerable individuals in acute danger
        r"\b(?:infants?|babys?|babies|children|child|kids?|elderly|seniors?|bedridden|pregnant|patients?|disabled)\s+(?:(?:are|is)\s+)?(?:stranded|trapped|stuck|in\s+danger)\b",
        r"\blife(?:\s+is)?\s+in\s+danger\b",
    ],
    "casualty": [
        r"\b(?:died|dead|death|fatalit(?:y|ies)|killed)\b",
        r"\b(?:severely\s+)?injured\b",
        r"\bmissing\s+(?:person|people|children|family)\b",
        r"\bcasualt(?:y|ies)\b",
        r"\bbodies\s+recovered\b",
    ],
    "water_ingress": [
        r"\b(?:flood\s*)?waters?\s+(?:is\s+)?(?:entering|flooding|filling)\s+(?:the\s+)?(?:houses?|homes?|buildings?|villages?|rooms?|ground\s+floors?)\b",
        r"\b(?:flood\s*)?waters?\s+inside\s+(?:the\s+)?(?:houses?|homes?|buildings?|rooms?)\b",
        r"\b(?:houses?|homes?|buildings?|villages?|ground\s+floors?)\s+(?:are\s+)?(?:submerged|inundated|under\s+water|flooding|filling\s+with\s+water)\b",
        r"\b(?:waist|chest|neck)\s+deep\s+water\b",
        r"\b(?:the\s+)?dam\s+(?:has\s+)?(?:burst|breached)\b",
        r"\bflash\s+flood(?:ing)?\b",
    ],
    "water_dynamics": [
        r"\b(?:flood\s*)?waters?\s+(?:levels?\s+)?(?:(?:is|are)\s+)?rising(?:\s+(?:rapidly|fast|quickly))?\b",
        r"\brising\s+(?:flood\s*)?waters?\b",
        r"\b(?:flood\s*)?waters?\s+levels?\s+(?:(?:is|are)\s+)?(?:rising|increasing)\b",
        r"\b(?:submerged|inundated|under\s+water)\b",
        r"\b(?:dam\s+burst|dam\s+breach|river\s+overflow(?:ed|ing)?)\b",
        r"\bflood\s+(?:warning|alert|watch)\b",
    ],
    "infrastructure_impact": [
        r"\b(?:(?:highway|railway)\s+)?(?:bridges?|roads?|highways?)\s+(?:(?:has\s+)?collapsed|washed\s+away|damaged|broken)\b",
        r"\b(?:bridges?|roads?|highways?)\s+(?:collapsed|washed\s+away|damaged|broken)\b",
        r"\b(?:roads?|highways?|access)\s+(?:is\s+)?(?:cut\s+off|blocked|impassable)\b",
        r"\b(?:power|electricity|grid|transformer)\s+(?:failure|cut|outage|down)\b",
        r"\b(?:hospital|clinic)\s+(?:flooded|submerged|without\s+power)\b",
        r"\bcommunication\s+(?:lines?\s+)?down\b",
    ],
    "evacuation_displacement": [
        r"\b(?:mandatory\s+)?evacuation\s+(?:order|in\s+progress|underway)\b",
        r"\b(?:evacuated|displaced)\s+(?:to\s+)?(?:safe\s+place|shelter|relief\s+camp)\b",
        r"\bpeople\s+in\s+shelter\s+facilities\b",
        r"\bhomes\s+abandoned\b",
    ],
}

# Contextual qualification patterns
NEGATION_PATTERNS = [
    r"\bno\s+(?:(?:one|person|people|residents?|citizens?)\s+(?:(?:are|is)\s+)?)?(?:actual\s+|real\s+|further\s+|major\s+|active\s+)?(?:flood|flooding|water\s+entering|trapped|stuck|casualties|damage|deaths?|injur(?:y|ies))\b",
    r"\bnot\s+(?:actually\s+|really\s+)?(?:flooded|trapped|stuck|submerged|in\s+danger)\b",
    r"\bwithout\s+(?:any\s+)?(?:actual\s+|real\s+)?(?:casualties|injuries|damage|flooding)\b",
    r"\bsituation\s+is\s+(?:normal|under\s+control|safe)\b",
    r"\bwater\s+(?:has\s+)?receded\b",
    r"\b(?:all|everyone)\s+(?:(?:is|are|were)\s+)?(?:safe|rescued|accounted\s+for)\b",
    r"\b(?:rescue\s+(?:teams?|crews?|workers?)|rescuers?|help)\s+(?:(?:have|has|is|are)\s+)?(?:already\s+)?(?:arrived|on\s+site|on\s+scene)\b",
]

HYPOTHETICAL_PATTERNS = [
    r"\bif\s+(?:the\s+)?(?:dam|river|water|flood|rain|people|children)\b",
    r"\bwhat\s+if\b",
    r"\bin\s+case\s+(?:of\s+)?(?:flooding|dam\s+burst|rain|getting\s+stuck)\b",
    r"\bcould\s+(?:cause|lead\s+to|flood)\b",
    r"\bmight\s+(?:overflow|burst|flood)\b",
]

HISTORICAL_PATTERNS = [
    r"\b(?:during|in|from|back\s+in)\s+(?:the\s+)?(?:19\d\d|200\d|201[0-9]|202[0-5])\b",
    r"\b(?:19\d\d|200\d|201[0-9]|202[0-5])\s+floods?\b",
    r"\b(?:last|previous)\s+year(?:'s)?\s+flood\b",
    r"\bremembering\s+(?:the\s+)?(?:flood|victims)\b",
    r"\banniversary\s+of\b",
    r"\byears?\s+ago\b",
]

SPECULATION_PATTERNS = [
    r"\brumou?rs?\s+(?:that|saying|circulating)\b",
    r"\bunconfirmed\s+(?:reports?|claims?)\b",
    r"\bhearing\s+that\b",
    r"\bnot\s+verified\b",
]


def extract_indicators(text: str) -> Dict[str, Any]:
    """
    Extract grounded, context-aware indicators from an emergency message.

    Returns:
    - active_indicators: Verified present-tense indicators (deduplicated by family)
    - active_evidence: Exact matched textual snippets
    - context_modifiers: Flags for negation, hypothetical, historical, speculation
    - discounted_indicators: Indicators flagged but suppressed due to context modifiers
    """
    if not isinstance(text, str):
        raise TypeError("Input text must be a string.")

    cleaned_text = text.lower().strip()
    if not cleaned_text:
        return {
            "active_indicators": {},
            "active_evidence": [],
            "context_modifiers": {
                "negated": False,
                "hypothetical": False,
                "historical": False,
                "speculation": False,
            },
            "discounted_indicators": {},
            "indicator_count": 0,
        }

    # 1. Detect contextual modifiers
    is_negated = any(bool(re.search(p, cleaned_text)) for p in NEGATION_PATTERNS)
    is_hypothetical = any(bool(re.search(p, cleaned_text)) for p in HYPOTHETICAL_PATTERNS)
    is_historical = any(bool(re.search(p, cleaned_text)) for p in HISTORICAL_PATTERNS)
    is_speculative = any(bool(re.search(p, cleaned_text)) for p in SPECULATION_PATTERNS)

    modifiers = {
        "negated": is_negated,
        "hypothetical": is_hypothetical,
        "historical": is_historical,
        "speculation": is_speculative,
    }

    # 2. Extract matched indicators per family
    raw_matches: Dict[str, List[str]] = {}
    for family, patterns in INDICATOR_PATTERNS.items():
        matched_spans: List[str] = []
        for pat in patterns:
            for match in re.finditer(pat, cleaned_text):
                matched_spans.append(match.group(0))
        if matched_spans:
            # Deduplicate matched snippets within family
            raw_matches[family] = list(dict.fromkeys(matched_spans))

    # 3. Apply qualification logic (anti-hallucination / context discounting)
    # If the message is explicitly negated, hypothetical, or purely historical,
    # indicators are routed to discounted_indicators to prevent false escalation.
    active_indicators: Dict[str, List[str]] = {}
    discounted_indicators: Dict[str, List[str]] = {}
    active_evidence: List[str] = []

    for family, spans in raw_matches.items():
        if is_negated or is_hypothetical or is_historical:
            discounted_indicators[family] = spans
        else:
            active_indicators[family] = spans
            active_evidence.extend(spans)

    return {
        "active_indicators": active_indicators,
        "active_evidence": list(dict.fromkeys(active_evidence)),
        "context_modifiers": modifiers,
        "discounted_indicators": discounted_indicators,
        "indicator_count": len(active_indicators),  # Canonical family count to avoid double-counting
    }
