"""
Pydantic Request and Response Schemas for MindScope REST API.
"""

from typing import Dict, Any, List, Optional, Literal
from pydantic import BaseModel, Field


class StudentProfileInput(BaseModel):
    age: int = Field(20, ge=15, le=25, description="Student age between 15 and 25")
    gender: Literal["Male", "Female", "Non-Binary"] = Field("Female", description="Gender identity")
    study_year: int = Field(2, ge=1, le=5, description="Year of study (1-5)")
    academic_pressure: float = Field(3.0, ge=1.0, le=5.0, description="Self-reported academic pressure (1-5)")
    study_hours: float = Field(4.0, ge=0.0, le=16.0, description="Daily self-study hours")
    sleep_hours: float = Field(6.5, ge=0.0, le=14.0, description="Nightly sleep duration in hours")
    screen_time_hours: float = Field(5.0, ge=0.0, le=18.0, description="Daily recreational screen time in hours")
    social_support: float = Field(3.0, ge=1.0, le=5.0, description="Perceived social support rating (1-5)")
    financial_stress: float = Field(2.5, ge=1.0, le=5.0, description="Perceived financial burden rating (1-5)")
    physical_activity_hours: float = Field(3.0, ge=0.0, le=20.0, description="Weekly physical activity hours")


class PredictionResponse(BaseModel):
    depression_risk_probability: float
    risk_category: str
    model_version: str
    is_diagnostic: bool = False
    medical_disclaimer: str


class FeatureContribution(BaseModel):
    feature: str
    display_name: str
    feature_value: float
    shap_value: float
    direction: str


class ExplainResponse(BaseModel):
    calibrated_probability: float
    base_value: float
    contributions: List[FeatureContribution]
    top_risk_escalators: List[FeatureContribution]
    top_protective_factors: List[FeatureContribution]
    plain_english_summary: str
    epistemic_warning: str
    medical_disclaimer: str


class WhatIfInput(BaseModel):
    baseline: Dict[str, float] = Field(
        default_factory=lambda: {
            "depression_score": 12.0,
            "attendance_rate": 85.0,
            "cgpa": 7.5,
        },
        description="Baseline student outcome metrics",
    )
    interventions: Dict[str, float] = Field(
        default_factory=lambda: {
            "sleep_hours": 1.5,
            "screen_time_hours": -1.5,
            "academic_pressure": -1.0,
        },
        description="Hypothetical delta shifts to apply to lifestyle/academic variables",
    )


class WhatIfResponse(BaseModel):
    baseline: Dict[str, float]
    interventions_applied: Dict[str, float]
    predicted_deltas: Dict[str, float]
    confidence_intervals_95: Dict[str, List[float]]
    counterfactual_outcomes: Dict[str, float]
    plain_english_summary: str
    causal_assumptions: str
    medical_disclaimer: str


class TextAnalysisInput(BaseModel):
    text: str = Field(..., min_length=1, description="Student reflection or narrative")


class TextAnalysisResponse(BaseModel):
    is_crisis: bool
    status: str
    message: Optional[str] = None
    emergency_helplines: Optional[Dict[str, str]] = None
    immediate_actions: Optional[List[str]] = None
    primary_emotion: Optional[str] = None
    emotion_probabilities: Optional[Dict[str, float]] = None
    distress_tier: Optional[str] = None
    topics_extracted: Optional[List[str]] = None
    medical_disclaimer: str


class AssistantInput(BaseModel):
    query: str = Field(..., min_length=1, description="Student inquiry or prompt")


class SourceMeta(BaseModel):
    title: str
    organization: str
    url: str


class AssistantResponse(BaseModel):
    is_crisis: bool
    is_diagnostic_refusal: bool
    response_text: str
    emergency_helplines: Optional[Dict[str, str]] = None
    sources_cited: List[SourceMeta]
    medical_disclaimer: str
