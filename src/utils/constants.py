"""
MindScope Constants and Safety Guidelines.
Verified Helplines and Regulatory Disclaimers.
"""

from typing import Final, Dict, Any

# Fixed Random Seed for Reproducibility across all experiments
RANDOM_SEED: Final[int] = 42

# Official, runtime-verified crisis helplines (India MoHFW & NIMHANS)
CRISIS_HELPLINES: Final[Dict[str, Dict[str, str]]] = {
    "tele_manas_short": {
        "name": "Tele-MANAS (Toll-Free Short Code)",
        "number": "14416",
        "description": "24/7 National Tele Mental Health Programme of India (MoHFW / NIMHANS)",
        "availability": "24x7, Free, Multilingual",
    },
    "tele_manas_toll_free": {
        "name": "Tele-MANAS (Toll-Free Alternate)",
        "number": "1800-891-4416",
        "description": "24/7 National Tele Mental Health Programme of India",
        "availability": "24x7, Free, Multilingual",
    },
    "national_emergency": {
        "name": "National Emergency Number",
        "number": "112",
        "description": "All-in-one emergency response service (Police, Fire, Ambulance)",
        "availability": "24x7",
    },
    "kiran": {
        "name": "KIRAN Mental Health Helpline",
        "number": "1800-599-0019",
        "description": "Ministry of Social Justice and Empowerment, Govt of India",
        "availability": "24x7, Toll-Free",
    },
    "vandrevala_foundation": {
        "name": "Vandrevala Foundation Helpline",
        "number": "+91 9999 666 555",
        "description": "Free psychological counselling and crisis intervention",
        "availability": "24x7",
    },
}

# Mandatory Research Disclaimer
MEDICAL_DISCLAIMER: Final[str] = (
    "MindScope is strictly an academic research and decision-support prototype. "
    "It is NOT a medical or clinical diagnostic instrument and does NOT provide medical diagnoses, "
    "clinical prognosis, or treatment recommendations. Never use this tool to replace professional "
    "psychological or psychiatric consultation. If you or someone you know is in crisis or distress, "
    "please immediately contact Tele-MANAS (14416 or 1800-891-4416) or call 112."
)
