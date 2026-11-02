"""
MindScope FastAPI Application.
Exposes REST endpoints for calibrated depression risk prediction, SHAP factor explainability,
causal what-if counterfactual simulation, affective NLP analysis, and safe grounded assistant.
"""

import os
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

# Workaround for OpenMP Windows compatibility
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from src.api.schemas import (
    StudentProfileInput,
    PredictionResponse,
    ExplainResponse,
    WhatIfInput,
    WhatIfResponse,
    TextAnalysisInput,
    TextAnalysisResponse,
    AssistantInput,
    AssistantResponse,
)
from src.causal.whatif import simulate_what_if_intervention
from src.explainability.explainer import MindScopeExplainer
from src.nlp.crisis_safeguard import check_crisis_indicators
from src.nlp.emotion_classifier import YouthEmotionClassifier
from src.assistant.safe_agent import SafeSupportAssistant
from src.utils.constants import MEDICAL_DISCLAIMER

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Application state container
app_state: Dict[str, Any] = {}


def initialize_app_state():
    """Load models, explainers, and safety engines into memory."""
    if app_state.get("initialized"):
        return

    # 1. Load calibrated depression classifier
    model_path = PROJECT_ROOT / "models" / "best_depression_classifier.joblib"
    if model_path.exists():
        app_state["model"] = joblib.load(model_path)
    else:
        app_state["model"] = None

    # 2. Load background data for SHAP explainer
    data_path = PROJECT_ROOT / "data" / "processed" / "students_clean.csv"
    if data_path.exists() and app_state["model"] is not None:
        bg_df = pd.read_csv(data_path)
        bg_sample = bg_df.sample(min(100, len(bg_df)), random_state=42)
        app_state["explainer"] = MindScopeExplainer(app_state["model"], bg_sample)
    else:
        app_state["explainer"] = None

    # 3. Initialize CPU Emotion Classifier
    narratives_path = PROJECT_ROOT / "data" / "nlp" / "youth_narratives.csv"
    if narratives_path.exists():
        df_narratives = pd.read_csv(narratives_path)
        app_state["emotion_classifier"] = YouthEmotionClassifier.train_baseline_pipeline(df_narratives)
    else:
        app_state["emotion_classifier"] = None

    # 4. Initialize Safe Support Assistant
    app_state["assistant"] = SafeSupportAssistant()
    app_state["initialized"] = True


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI."""
    initialize_app_state()
    yield
    app_state.clear()


# Pre-initialize so models are ready immediately for any testing context
initialize_app_state()

app = FastAPI(
    title="MindScope AI Research API",
    description=(
        "Full-Stack Explainable & Causal AI Research Platform for Youth Mental Health Issues. "
        "Strictly Non-Diagnostic Research Decision-Support System."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for Next.js frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["System"])
def health_check() -> Dict[str, Any]:
    """Service health status and artifact readiness check."""
    return {
        "status": "healthy",
        "service": "MindScope Research API",
        "version": "1.0.0",
        "model_loaded": app_state.get("model") is not None,
        "explainer_ready": app_state.get("explainer") is not None,
        "emotion_classifier_ready": app_state.get("emotion_classifier") is not None,
        "assistant_ready": app_state.get("assistant") is not None,
        "medical_disclaimer": MEDICAL_DISCLAIMER,
    }


@app.post("/predict", response_model=PredictionResponse, tags=["Predictive Analytics"])
def predict_depression_risk(profile: StudentProfileInput) -> PredictionResponse:
    """Predict calibrated probability of depression risk."""
    model = app_state.get("model")
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Predictive model artifact not loaded on server.",
        )

    df_input = pd.DataFrame([profile.model_dump()])

    try:
        probs = model.predict_proba(df_input)[0]
        prob_depressed = float(probs[1])

        if prob_depressed >= 0.65:
            risk_cat = "High Risk"
        elif prob_depressed >= 0.35:
            risk_cat = "Moderate Risk"
        else:
            risk_cat = "Low Risk"

        return PredictionResponse(
            depression_risk_probability=round(prob_depressed, 4),
            risk_category=risk_cat,
            model_version="Calibrated-LogisticRegression-v1.0",
            is_diagnostic=False,
            medical_disclaimer=MEDICAL_DISCLAIMER,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference error: {str(e)}",
        )


@app.post("/explain", response_model=ExplainResponse, tags=["Explainability"])
def explain_student_risk(profile: StudentProfileInput) -> ExplainResponse:
    """Generate SHAP local attribution breakdown and factor summaries."""
    explainer = app_state.get("explainer")
    if explainer is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="SHAP explainer engine not initialized.",
        )

    try:
        raw_dict = profile.model_dump()
        explanation = explainer.explain_single_student(raw_dict)

        return ExplainResponse(
            calibrated_probability=round(float(explanation["predicted_risk_probability"]), 4),
            base_value=round(float(explanation["base_value"]), 4),
            contributions=explanation["all_feature_contributions"],
            top_risk_escalators=explanation["top_risk_escalators"],
            top_protective_factors=explanation["top_protective_factors"],
            plain_english_summary=explanation["plain_english_summary"],
            epistemic_warning=explanation["epistemic_guardrail"],
            medical_disclaimer=MEDICAL_DISCLAIMER,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Explainability computation failed: {str(e)}",
        )


@app.post("/whatif", response_model=WhatIfResponse, tags=["Causal Inference"])
def counterfactual_what_if(payload: WhatIfInput) -> WhatIfResponse:
    """Simulate causal impacts of proposed behavioral or academic interventions."""
    try:
        results = simulate_what_if_intervention(
            student_profile=payload.baseline,
            interventions=payload.interventions,
        )

        deltas = {k: v["delta"] for k, v in results["counterfactual_outcomes"].items()}
        ci_95 = {k: v["ci_95"] for k, v in results["counterfactual_outcomes"].items()}
        outcomes = {k: v["estimated_value"] for k, v in results["counterfactual_outcomes"].items()}

        return WhatIfResponse(
            baseline=results["baseline"],
            interventions_applied=results["interventions_applied"],
            predicted_deltas=deltas,
            confidence_intervals_95=ci_95,
            counterfactual_outcomes=outcomes,
            plain_english_summary=results["plain_english_narrative"],
            causal_assumptions="; ".join(results["causal_assumptions"]),
            medical_disclaimer=MEDICAL_DISCLAIMER,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Causal simulation failed: {str(e)}",
        )


@app.post("/analyze-text", response_model=TextAnalysisResponse, tags=["Affective NLP"])
def analyze_student_text(payload: TextAnalysisInput) -> TextAnalysisResponse:
    """Analyze student narrative for emotional valence, distress tier, and latent topics."""
    text = payload.text.strip()
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reflection text cannot be empty.",
        )

    # 1. Deterministic Crisis Safeguard Check
    is_crisis, crisis_payload = check_crisis_indicators(text)
    if is_crisis:
        return TextAnalysisResponse(
            is_crisis=True,
            status=crisis_payload.get("status", "CRISIS_SAFEGUARD_ACTIVATED"),
            message=crisis_payload.get("message"),
            emergency_helplines=crisis_payload.get("emergency_helplines"),
            immediate_actions=crisis_payload.get("immediate_actions"),
            primary_emotion=None,
            emotion_probabilities=None,
            distress_tier="Acute Crisis",
            topics_extracted=["Urgent Crisis / Self-Harm"],
            medical_disclaimer=MEDICAL_DISCLAIMER,
        )

    # 2. Emotion Classifier
    classifier = app_state.get("emotion_classifier")
    if classifier is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Emotion classification model not initialized.",
        )

    result = classifier.predict_emotion(text)
    
    words = [w.lower() for w in text.split() if len(w) > 4]
    topics = list(dict.fromkeys(words[:5])) if words else ["General Reflection"]

    return TextAnalysisResponse(
        is_crisis=False,
        status="ANALYSIS_COMPLETE",
        message="Text analyzed successfully for emotional markers.",
        emergency_helplines=None,
        immediate_actions=None,
        primary_emotion=result.get("primary_emotion_label", result.get("primary_emotion")),
        emotion_probabilities=result.get("emotion_probabilities"),
        distress_tier=result.get("distress_tier"),
        topics_extracted=topics,
        medical_disclaimer=MEDICAL_DISCLAIMER,
    )


@app.post("/assistant", response_model=AssistantResponse, tags=["Support Assistant"])
def chat_with_assistant(payload: AssistantInput) -> AssistantResponse:
    """Safe, source-grounded support assistant using local ChromaDB RAG."""
    assistant: SafeSupportAssistant = app_state.get("assistant")
    if assistant is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Support assistant service not initialized.",
        )

    query = payload.query.strip()
    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty.",
        )

    response_data = assistant.respond(query)

    return AssistantResponse(
        is_crisis=response_data.get("is_crisis", False),
        is_diagnostic_refusal=response_data.get("is_diagnostic_refusal", False),
        response_text=response_data.get("response_text", response_data.get("message", "")),
        emergency_helplines=response_data.get("emergency_helplines"),
        sources_cited=response_data.get("sources_cited", []),
        medical_disclaimer=MEDICAL_DISCLAIMER,
    )
