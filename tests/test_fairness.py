"""
Unit Tests for Algorithmic Fairness and Subgroup Parity (Phase 8).
Validates that model predictions comply with Four-Fifths (80%) rules
across gender and age cohorts without disparate impact.
"""

import pytest
from src.fairness.audit import run_fairness_audit, categorize_age_group


@pytest.fixture(scope="module")
def audit_results():
    return run_fairness_audit()


def test_age_categorization():
    """Test age discretization bounds."""
    assert categorize_age_group(16) == "Adolescent (15-18)"
    assert categorize_age_group(18) == "Adolescent (15-18)"
    assert categorize_age_group(19) == "Early Undergraduate (19-21)"
    assert categorize_age_group(21) == "Early Undergraduate (19-21)"
    assert categorize_age_group(22) == "Senior / Post-Grad (22-25)"
    assert categorize_age_group(25) == "Senior / Post-Grad (22-25)"


def test_gender_parity_metrics(audit_results):
    """Verify gender demographic parity and equal opportunity ratios exceed 0.80."""
    disp = audit_results["disparate_impact_analysis"]
    assert disp["gender_demographic_parity_ratio"] >= 0.80, (
        f"Gender Demographic Parity ratio {disp['gender_demographic_parity_ratio']} failed 80% rule"
    )
    assert disp["gender_equal_opportunity_ratio"] >= 0.80, (
        f"Gender Equal Opportunity ratio {disp['gender_equal_opportunity_ratio']} failed 80% rule"
    )


def test_age_parity_metrics(audit_results):
    """Verify age demographic parity and equal opportunity ratios exceed 0.80."""
    disp = audit_results["disparate_impact_analysis"]
    assert disp["age_demographic_parity_ratio"] >= 0.80, (
        f"Age Demographic Parity ratio {disp['age_demographic_parity_ratio']} failed 80% rule"
    )
    assert disp["age_equal_opportunity_ratio"] >= 0.80, (
        f"Age Equal Opportunity ratio {disp['age_equal_opportunity_ratio']} failed 80% rule"
    )


def test_subgroup_calibration_adequacy(audit_results):
    """Verify all subgroup Brier scores remain well-calibrated (< 0.15)."""
    assert audit_results["fairness_verdict"]["calibration_adequate"] is True
    for g, metrics in audit_results["gender_audit"].items():
        assert metrics["brier_score"] < 0.10, f"Gender {g} calibration Brier score too high: {metrics['brier_score']}"
    for ag, metrics in audit_results["age_group_audit"].items():
        assert metrics["brier_score"] < 0.10, f"Age group {ag} calibration Brier score too high: {metrics['brier_score']}"


def test_overall_fairness_verdict(audit_results):
    """Confirm overall fairness verdict passes."""
    assert audit_results["fairness_verdict"]["overall_fairness_passed"] is True
