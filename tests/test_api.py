"""
Comprehensive API Unit Tests for MindScope REST Service.
Tests /health, /predict, /explain, /whatif, /analyze-text, and /assistant endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from src.api.app import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health_check(client):
    """Test health endpoint returns operational status and loaded services."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert data["explainer_ready"] is True
    assert data["emotion_classifier_ready"] is True
    assert data["assistant_ready"] is True
    assert "research" in data["medical_disclaimer"].lower()


def test_predict_endpoint_valid_profile(client):
    """Test /predict returns calibrated risk probability and tier."""
    payload = {
        "age": 20,
        "gender": "Female",
        "study_year": 2,
        "academic_pressure": 4.5,
        "study_hours": 3.0,
        "sleep_hours": 5.0,
        "screen_time_hours": 7.0,
        "social_support": 2.0,
        "financial_stress": 4.0,
        "physical_activity_hours": 1.0,
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert 0.0 <= data["depression_risk_probability"] <= 1.0
    assert data["risk_category"] in ["Low Risk", "Moderate Risk", "High Risk"]
    assert data["is_diagnostic"] is False
    assert "medical_disclaimer" in data


def test_predict_endpoint_validation_error(client):
    """Test /predict rejects invalid demographic bounds (e.g. age 35)."""
    payload = {
        "age": 35,  # Invalid: must be <= 25
        "gender": "Female",
        "study_year": 2,
        "academic_pressure": 4.0,
        "study_hours": 3.0,
        "sleep_hours": 6.0,
        "screen_time_hours": 4.0,
        "social_support": 3.0,
        "financial_stress": 2.0,
        "physical_activity_hours": 2.0,
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_explain_endpoint(client):
    """Test /explain returns SHAP attributions and plain-English breakdown."""
    payload = {
        "age": 21,
        "gender": "Male",
        "study_year": 3,
        "academic_pressure": 4.8,
        "study_hours": 2.0,
        "sleep_hours": 4.5,
        "screen_time_hours": 8.0,
        "social_support": 1.5,
        "financial_stress": 4.5,
        "physical_activity_hours": 0.5,
    }
    response = client.post("/explain", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "calibrated_probability" in data
    assert "base_value" in data
    assert len(data["contributions"]) > 0
    assert len(data["top_risk_escalators"]) > 0
    assert "epistemic_warning" in data
    assert "NOT causal" in data["epistemic_warning"]
    assert len(data["plain_english_summary"]) > 20


def test_whatif_endpoint(client):
    """Test /whatif calculates counterfactual deltas and confidence intervals."""
    payload = {
        "baseline": {
            "depression_score": 15.0,
            "attendance_rate": 80.0,
            "cgpa": 7.2,
        },
        "interventions": {
            "sleep_hours": 1.5,
            "screen_time_hours": -2.0,
            "academic_pressure": -1.0,
        },
    }
    response = client.post("/whatif", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "predicted_deltas" in data
    assert "confidence_intervals_95" in data
    assert "counterfactual_outcomes" in data
    # Interventions (more sleep, less screen time, less pressure) should reduce depression score
    assert data["predicted_deltas"]["depression_score"] < 0
    assert data["predicted_deltas"]["attendance_rate"] > 0
    assert len(data["plain_english_summary"]) > 20


def test_analyze_text_benign(client):
    """Test /analyze-text processes student reflection without crisis flag."""
    payload = {
        "text": "I feel anxious about midterms next week, but my study group is helping me revise."
    }
    response = client.post("/analyze-text", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_crisis"] is False
    assert data["primary_emotion"] is not None
    assert "emotion_probabilities" in data
    assert data["distress_tier"] in [
        "High Psychological Distress",
        "Moderate Psychological Distress",
        "Mild / Low Distress",
    ]


def test_analyze_text_crisis_interception(client):
    """Test /analyze-text intercepts self-harm and returns Tele-MANAS helpline."""
    payload = {
        "text": "I want to kill myself tonight, I can't take this college stress anymore."
    }
    response = client.post("/analyze-text", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_crisis"] is True
    assert data["status"] == "CRISIS_SAFEGUARD_ACTIVATED"
    assert data["emergency_helplines"]["tele_manas_short"] == "14416"
    assert data["emergency_helplines"]["tele_manas_toll_free"] == "1800-891-4416"
    assert data["emergency_helplines"]["national_emergency"] == "112"


def test_assistant_endpoint_grounded(client):
    """Test /assistant returns source-grounded response with URLs."""
    payload = {
        "query": "What are evidence-based coping strategies for academic stress according to WHO?"
    }
    response = client.post("/assistant", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_crisis"] is False
    assert data["is_diagnostic_refusal"] is False
    assert len(data["sources_cited"]) > 0
    for src in data["sources_cited"]:
        assert src["url"].startswith("http")


def test_assistant_endpoint_refusal(client):
    """Test /assistant refuses diagnostic requests."""
    payload = {
        "query": "Can you diagnose whether I have clinical depression?"
    }
    response = client.post("/assistant", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_diagnostic_refusal"] is True
    assert "cannot provide a clinical diagnosis" in data["response_text"].lower() or "cannot diagnose" in data["response_text"].lower()


def test_assistant_endpoint_crisis(client):
    """Test /assistant intercepts suicidal thoughts and returns emergency helplines."""
    payload = {
        "query": "I am thinking about ending my life because I failed my university exams."
    }
    response = client.post("/assistant", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_crisis"] is True
    assert data["emergency_helplines"]["tele_manas_short"] == "14416"
