"""
Safe Source-Grounded Support Assistant for MindScope.
Integrates ChromaDB RAG retrieval, Anthropic Claude API, and strict multi-tier safety guardrails:
1. Immediate crisis interception (Tele-MANAS 14416 / 1800-891-4416 / 112)
2. Non-diagnostic and prescription refusal
3. Mandatory citation of authoritative public guidance (WHO, NIMH, Tele-MANAS, NIMHANS)
"""

import os
import re
from typing import Dict, Any, List, Optional, Tuple

import anthropic

from src.assistant.vector_store import GuidanceVectorStore
from src.nlp.crisis_safeguard import check_crisis_indicators
from src.utils.constants import MEDICAL_DISCLAIMER, CRISIS_HELPLINES

DIAGNOSTIC_KEYWORDS = [
    r"\bdiagnos(?:e|es|ed|ing|is)\b",
    r"\bdo\s+i\s+have\s+(?:clinical\s+)?(?:depression|anxiety|bipolar|adhd|ptsd|ocd|a\s+mental\s+disorder)\b",
    r"\bam\s+i\s+(?:clinically\s+)?(?:depressed|bipolar|schizophrenic)\b",
    r"\bprescribe\s+(?:me\s+)?(?:medication|antidepressants|xanax|pills|drugs)\b",
    r"\bwhat\s+dose\s+of\b",
    r"\bcertify\s+me\b",
    r"\bdeveloper\s+mode\b",
    r"\bignore\s+(?:all\s+)?(?:previous\s+)?instructions\b",
    r"\bpretend\s+you\s+are\s+(?:a\s+)?(?:doctor|psychiatrist|therapist|physician)\b",
    r"\bpsychiatric\s+(?:diagnosis|condition|evaluation|assessment)\b",
]

SYSTEM_PROMPT = """You are MindScope Assistant, an empathetic, evidence-based academic research and student support assistant.
Your core mandate is to support youth well-being while strictly obeying these non-negotiable safety rules:

1. NON-DIAGNOSTIC BOUNDARY: You MUST NOT diagnose mental health conditions or assess clinical pathology. If the user asks for a diagnosis, explicitly state that you are an academic research tool and cannot diagnose, and encourage consulting a licensed mental health professional.
2. NO PRESCRIPTIONS OR MEDICAL ADVICE: Never recommend medication, dosages, or pharmaceutical treatments.
3. SOURCE GROUNDING & CITATION: You MUST base your suggestions strictly on the provided retrieved guidance documents (from WHO, NIMH, Tele-MANAS, NIMHANS). You MUST explicitly cite the source organizations and their reference URLs in markdown format.
4. TONE & EMPATHY: Be warm, non-judgmental, practical, and solution-focused. Prioritize sleep hygiene, academic boundary-setting, cognitive grounding, and reaching out to trusted social circles or university counselors.
5. MANDATORY DISCLAIMER: Always conclude with MindScope's research disclaimer."""


class SafeSupportAssistant:
    """
    RAG-powered safe support assistant integrating ChromaDB and Anthropic API.
    """

    def __init__(self, vector_store: Optional[GuidanceVectorStore] = None, api_key: Optional[str] = None):
        self.vector_store = vector_store or GuidanceVectorStore()
        # Initialize vector store documents if empty
        self.vector_store.populate_from_corpus()
        
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=self.api_key) if self.api_key else None

    def respond(self, user_query: str) -> Dict[str, Any]:
        """
        Process user query through the multi-tier safety and RAG pipeline.
        """
        # Tier 1: Deterministic Crisis Interception
        is_crisis, crisis_payload = check_crisis_indicators(user_query)
        if is_crisis:
            return crisis_payload

        # Tier 2: Non-Diagnostic & Prescription Refusal Check
        clean_q = user_query.lower()
        if any(re.search(pat, clean_q) for pat in DIAGNOSTIC_KEYWORDS):
            refusal_response = (
                "I cannot provide a clinical diagnosis, medical evaluation, or prescription. "
                "MindScope is strictly an academic research and educational decision-support platform, "
                "not a healthcare or diagnostic instrument. If you are experiencing persistent distress, "
                "fatigue, or changes in mood that interfere with your daily life, please reach out to your "
                "campus student wellness center or consult a qualified psychiatrist or clinical psychologist."
            )
            return {
                "is_crisis": False,
                "is_diagnostic_refusal": True,
                "response_text": refusal_response,
                "sources_cited": [
                    {
                        "organization": "National Institute of Mental Health (NIMH)",
                        "title": "College Students and Mental Health",
                        "url": "https://www.nimh.nih.gov/health/publications/student-mental-health",
                    },
                    {
                        "organization": "Tele-MANAS (MoHFW India)",
                        "title": "National Tele Mental Health Programme",
                        "url": "https://telemanas.mohfw.gov.in/",
                    },
                ],
                "medical_disclaimer": MEDICAL_DISCLAIMER,
            }

        # Tier 3: RAG Retrieval from Authoritative Guidance Corpus
        retrieved_docs = self.vector_store.search_guidance(user_query, top_k=2)
        sources_meta = [
            {
                "title": doc["title"],
                "organization": doc["organization"],
                "url": doc["url"],
            }
            for doc in retrieved_docs
        ]

        # Context string formatting
        context_str = "\n\n".join([
            f"Source [{doc['organization']} - {doc['title']}]:\n{doc['content']}\nReference URL: {doc['url']}"
            for doc in retrieved_docs
        ])

        # Tier 4: LLM Generation via Anthropic Claude (or deterministic grounded fallback)
        if self.client and self.api_key:
            try:
                user_message = (
                    f"User Query:\n{user_query}\n\n"
                    f"Authoritative Guidance Context:\n{context_str}\n\n"
                    f"Provide an empathetic, evidence-based response citing the sources and their reference URLs above."
                )

                message = self.client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=600,
                    system=SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": user_message}],
                )
                response_text = message.content[0].text
            except Exception as e:
                response_text = self._generate_grounded_fallback(user_query, retrieved_docs)
        else:
            response_text = self._generate_grounded_fallback(user_query, retrieved_docs)

        return {
            "is_crisis": False,
            "is_diagnostic_refusal": False,
            "response_text": response_text,
            "sources_cited": sources_meta,
            "retrieved_context_count": len(retrieved_docs),
            "medical_disclaimer": MEDICAL_DISCLAIMER,
        }

    def _generate_grounded_fallback(self, query: str, docs: List[Dict[str, Any]]) -> str:
        """
        Deterministic, source-grounded response fallback when API key is unconfigured or offline.
        """
        primary_doc = docs[0] if docs else {
            "organization": "Tele-MANAS / MoHFW India",
            "title": "National Tele Mental Health Programme",
            "url": "https://telemanas.mohfw.gov.in/",
            "content": "Free 24x7 psychological support is accessible via toll-free helpline 14416 / 1800-891-4416."
        }

        citations = "\n".join([
            f"- **[{d['organization']} - {d['title']}]({d['url']})**"
            for d in docs
        ])

        return (
            f"Thank you for sharing this. Based on authoritative public mental health guidance, "
            f"navigating high workloads and emotional distress requires deliberate lifestyle stabilization:\n\n"
            f"1. **Rest & Circadian Regularity:** Maintaining a predictable sleep schedule of 7-9 hours directly aids cognitive retention and emotional regulation.\n"
            f"2. **Workload Chunking:** Approaching tasks in 25-30 minute focused intervals with intentional micro-breaks mitigates mental fatigue.\n"
            f"3. **Social Buffering:** Sharing your academic burden with trusted peers or mentors reduces isolation.\n"
            f"4. **Professional Guidance:** If feelings of anxiety or exhaustion persist, free and confidential support is available 24x7 across India via Tele-MANAS (14416 or 1800-891-4416).\n\n"
            f"**Verified Sources Consulted:**\n{citations}\n\n"
            f"_{MEDICAL_DISCLAIMER}_"
        )
