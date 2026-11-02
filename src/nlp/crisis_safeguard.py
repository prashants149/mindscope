"""
Deterministic Crisis Safeguard and Red-Line Interceptor for MindScope.
Immediately halts analytical processing and surfaces verified emergency helplines
if suicidal ideation, self-harm, or severe crisis is detected.
"""

import re
from typing import Dict, Any, Tuple
from src.utils.constants import CRISIS_HELPLINES, MEDICAL_DISCLAIMER

# Strict regex patterns for self-harm and suicide detection
CRISIS_PATTERNS = [
    r"\b(?:kill|killing)\s+(?:myself|me)\b",
    r"\b(?:end|ending)\s+(?:my\s+life|it\s+all)\b",
    r"\b(?:want|wish)\s+to\s+die\b",
    r"\b(?:suicide|suicidal)\b",
    r"\b(?:cut|cutting)\s+(?:myself|my\s+wrists)\b",
    r"\b(?:cut|cutting)\b.*?\b(?:wrist|wrists|vein|veins)\b",
    r"\bcutting\s+techniques\b",
    r"\bhang(?:ing)?\s+(?:myself|oneself)\b",
    r"\b(?:self[\s\-]harm|harming\s+myself)\b",
    r"\bbetter\s+off\s+dead\b",
    r"\bdon'?t\s+want\s+to\s+live\s+anymore\b",
    r"\bno\s+reason\s+to\s+live\b",
    r"\btake\s+my\s+own\s+life\b",
    r"\boverdose\s+on\b",
    r"\b(?:methods?|ways?|techniques?)\s+(?:to|of|for)\s+(?:commit\s+suicide|kill\s+(?:myself|oneself)|self[\s\-]harm|dying)\b",
]

# Exceptions to prevent false positives on common campus idioms (e.g., "killed that exam")
FALSE_POSITIVE_EXCEPTIONS = [
    r"\bkilled\s+(?:that|the|my)\s+(?:exam|presentation|interview|test|quiz)\b",
    r"\bkilling\s+it\b",
    r"\bdie\s+laughing\b",
    r"\bto\s+die\s+for\b",
]


def check_crisis_indicators(text: str) -> Tuple[bool, Dict[str, Any]]:
    """
    Evaluate user text for crisis signals.
    If crisis is detected, returns (True, supportive_response_payload).
    Otherwise returns (False, {}).
    """
    clean_text = text.lower().strip()

    # First check for benign campus idioms
    for fp_pattern in FALSE_POSITIVE_EXCEPTIONS:
        if re.search(fp_pattern, clean_text):
            # If the only match is an idiom, do not flag unless explicit suicidal intent is also present
            if not any(
                re.search(p, clean_text)
                for p in [r"\bkill\s+myself\b", r"\bsuicide\b", r"\bend\s+my\s+life\b"]
            ):
                return False, {}

    # Check for acute crisis patterns
    is_crisis = False
    matched_patterns = []
    for pattern in CRISIS_PATTERNS:
        match = re.search(pattern, clean_text)
        if match:
            is_crisis = True
            matched_patterns.append(match.group(0))

    if is_crisis:
        crisis_response = {
            "is_crisis": True,
            "status": "CRISIS_SAFEGUARD_ACTIVATED",
            "message": (
                "We noticed that your message expresses severe emotional distress or thoughts of self-harm. "
                "Your safety and well-being are paramount. Please know that you are not alone, "
                "and compassionate, confidential support is available right now."
            ),
            "emergency_helplines": {
                "tele_manas_short": CRISIS_HELPLINES["tele_manas_short"]["number"],
                "tele_manas_toll_free": CRISIS_HELPLINES["tele_manas_toll_free"]["number"],
                "national_emergency": CRISIS_HELPLINES["national_emergency"]["number"],
                "kiran_helpline": CRISIS_HELPLINES["kiran"]["number"],
                "vandrevala_foundation": CRISIS_HELPLINES["vandrevala_foundation"]["number"],
            },
            "immediate_actions": [
                "Call Tele-MANAS toll-free at 14416 or 1800-891-4416 (24x7, Free, Multilingual support across India).",
                "Call National Emergency Services at 112 if you are in immediate danger.",
                "Reach out to a trusted family member, close friend, or campus student counselor right now.",
                "Do not stay alone if you are feeling overwhelmed.",
            ],
            "medical_disclaimer": MEDICAL_DISCLAIMER,
        }
        return True, crisis_response

    return False, {}
