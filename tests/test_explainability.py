"""
Unit tests for SHAP Explainability Engine and Epistemic Guardrails.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
import numpy as np
import pandas as pd
import joblib

from src.explainability.explainer import (
    MindScopeExplainer,
    EPISTEMIC_GUARDRAIL_NOTICE,
    FEATURE_LABEL_MAP,
)
from src.data.generator import generate_synthetic_dataset
from src.models.pipeline import get_model_specs, wrap_with_calibration


@pytest.fixture(scope="module")
def sample_explainer_and_data():
    df, _ = generate_synthetic_dataset(n_samples=400, random_seed=42)
    feature_cols = [
        "age", "study_year", "sleep_hours", "screen_time_hours",
        "academic_pressure", "social_support", "financial_stress",
        "physical_activity_hours", "gender"
    ]
    X = df[feature_cols]
    y = df["depression"].values

    # Fit a quick model pipeline for testing
    models = get_model_specs()
    pipe = models["Logistic_Regression"]
    pipe.fit(X, y)
    calibrated = wrap_with_calibration(pipe, cv=2, method="sigmoid")
    calibrated.fit(X, y)

    explainer = MindScopeExplainer(model_pipeline=calibrated, background_df=df.iloc[:100])
    return explainer, df


def test_explainer_feature_names(sample_explainer_and_data):
    """Verify feature names are cleanly extracted and mapped."""
    explainer, _ = sample_explainer_and_data
    assert "academic_pressure" in explainer.transformed_names
    assert "sleep_hours" in explainer.transformed_names
    assert "Academic Pressure (1-5)" in explainer.display_names
    assert "Sleep Duration (hrs/night)" in explainer.display_names


def test_global_importance_sorting(sample_explainer_and_data):
    """Verify global importance rankings are properly sorted in descending order."""
    explainer, df = sample_explainer_and_data
    ranking = explainer.get_global_importance(df.iloc[100:200])

    assert len(ranking) == len(explainer.transformed_names)
    importances = [item["mean_abs_shap"] for item in ranking]
    
    # Assert monotonically non-increasing
    assert all(importances[i] >= importances[i+1] for i in range(len(importances)-1))
    # Top features should have non-zero impact
    assert importances[0] > 0.05


def test_single_student_explanation_structure(sample_explainer_and_data):
    """Verify local explanation structure, fields, and values."""
    explainer, _ = sample_explainer_and_data
    student = {
        "student_id": "STU_TEST",
        "age": 20,
        "gender": "Female",
        "study_year": 2,
        "sleep_hours": 5.0,
        "screen_time_hours": 8.0,
        "academic_pressure": 5,
        "social_support": 1,
        "financial_stress": 4,
        "physical_activity_hours": 1.0,
    }
    
    res = explainer.explain_single_student(student)

    assert 0.0 <= res["predicted_risk_probability"] <= 1.0
    assert res["risk_tier"] in ["Elevated Risk Indicator", "Moderate Risk Indicator", "Low Risk Indicator"]
    assert "plain_english_summary" in res
    assert len(res["plain_english_summary"]) > 20
    
    # Check that risk factors have positive SHAP and protective have negative SHAP
    for factor in res["top_risk_escalators"]:
        assert factor["shap_value"] > 0
    for factor in res["top_protective_factors"]:
        assert factor["shap_value"] < 0


def test_epistemic_causal_guardrail_presence(sample_explainer_and_data):
    """Verify that every explanation explicitly includes the 'associations are not causes' guardrail."""
    explainer, _ = sample_explainer_and_data
    student = {
        "student_id": "STU_TEST_2",
        "age": 22,
        "gender": "Male",
        "study_year": 4,
        "sleep_hours": 7.5,
        "screen_time_hours": 4.0,
        "academic_pressure": 2,
        "social_support": 4,
        "financial_stress": 2,
        "physical_activity_hours": 4.0,
    }
    res = explainer.explain_single_student(student)

    # Strictly test presence of causal warning
    assert "epistemic_guardrail" in res
    assert "NOT causal" in res["epistemic_guardrail"] or "not causes" in res["epistemic_guardrail"].lower()
    assert "medical_disclaimer" in res
