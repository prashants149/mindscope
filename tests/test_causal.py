"""
Unit tests for Causal Inference Engine, DoWhy/EconML Estimators, and What-If Simulator.

NOTE: DoWhy/sympy/gmpy2 imports trigger a Windows fatal exception (code 0xc0000139)
during pytest collection when loaded in a background thread. We therefore import
all DoWhy-dependent modules lazily inside fixtures/test functions, never at module
level, to avoid the crash.
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

# Lazy-loaded causal modules (imported inside fixtures to avoid DoWhy DLL crash at collection)
def _get_causal_graph():
    from src.causal.graph import get_causal_dag_dot
    return get_causal_dag_dot

def _get_estimator():
    from src.causal.estimator import run_single_causal_pipeline, BACKDOOR_CONFOUNDERS, CAUSAL_TOLERANCES
    return run_single_causal_pipeline, BACKDOOR_CONFOUNDERS, CAUSAL_TOLERANCES

def _get_whatif():
    from src.causal.whatif import simulate_what_if_intervention
    return simulate_what_if_intervention

def _get_subgroups():
    from src.causal.subgroups import analyze_subgroup_causal_effects
    return analyze_subgroup_causal_effects

from src.data.generator import generate_synthetic_dataset, GROUND_TRUTH_EFFECTS


@pytest.fixture(scope="module")
def causal_dataset():
    df, _ = generate_synthetic_dataset(n_samples=1000, random_seed=42)
    return df


def test_causal_dag_structure():
    """Verify DOT graph contains key nodes and causal edges."""
    get_causal_dag_dot = _get_causal_graph()
    dag_dot = get_causal_dag_dot()
    assert "sleep_hours -> depression_score" in dag_dot
    assert "academic_pressure -> depression_score" in dag_dot
    assert "depression_score -> attendance_rate" in dag_dot
    assert "depression_score -> cgpa" in dag_dot


def test_sleep_to_depression_causal_recovery(causal_dataset):
    """Verify DoWhy & EconML estimate recovers ground truth within tolerance."""
    run_single_causal_pipeline, BACKDOOR_CONFOUNDERS, CAUSAL_TOLERANCES = _get_estimator()
    gt = GROUND_TRUTH_EFFECTS
    true_beta = gt.beta_sleep_on_dep  # -1.50
    tolerance = CAUSAL_TOLERANCES["sleep_hours -> depression_score"]  # 0.15

    res = run_single_causal_pipeline(
        df=causal_dataset,
        treatment="sleep_hours",
        outcome="depression_score",
        common_causes=BACKDOOR_CONFOUNDERS["sleep_hours -> depression_score"],
        run_refutations=True,
    )

    est = res["dowhy_estimate"]
    abs_err = abs(est - true_beta)

    assert abs_err <= tolerance, f"Estimate {est} differs from true {true_beta} by {abs_err} (tolerance {tolerance})"
    assert res["refutations"]["placebo_treatment"]["passed"] is True


def test_academic_pressure_to_depression_causal_recovery(causal_dataset):
    """Verify academic pressure causal estimate recovers ground truth within tolerance."""
    run_single_causal_pipeline, BACKDOOR_CONFOUNDERS, CAUSAL_TOLERANCES = _get_estimator()
    gt = GROUND_TRUTH_EFFECTS
    true_beta = gt.beta_acad_on_dep  # +2.20
    tolerance = CAUSAL_TOLERANCES["academic_pressure -> depression_score"]  # 0.18

    res = run_single_causal_pipeline(
        df=causal_dataset,
        treatment="academic_pressure",
        outcome="depression_score",
        common_causes=BACKDOOR_CONFOUNDERS["academic_pressure -> depression_score"],
        run_refutations=False,
    )

    est = res["dowhy_estimate"]
    abs_err = abs(est - true_beta)
    assert abs_err <= tolerance, f"Estimate {est} differs from true {true_beta} by {abs_err}"


def test_whatif_simulator_direction_and_confidence_intervals():
    """Verify What-If simulation outputs correct sign shifts and valid 95% CIs."""
    simulate_what_if_intervention = _get_whatif()
    student = {
        "student_id": "STU_TEST",
        "depression_score": 15.0,
        "attendance_rate": 80.0,
        "cgpa": 7.0,
    }

    # Positive lifestyle intervention: +2 hrs sleep, -1 pressure
    interventions = {
        "sleep_hours": 2.0,
        "academic_pressure": -1.0,
    }

    res = simulate_what_if_intervention(student, interventions)

    # Depression delta should be negative (improvement)
    dep_res = res["counterfactual_outcomes"]["depression_score"]
    assert dep_res["delta"] < -4.0
    assert dep_res["estimated_value"] < 15.0
    assert dep_res["ci_95"][0] < dep_res["ci_95"][1]

    # Attendance delta should be positive (improvement)
    att_res = res["counterfactual_outcomes"]["attendance_rate"]
    assert att_res["delta"] > 0
    assert att_res["ci_95"][0] < att_res["ci_95"][1]

    # CGPA delta should be positive (improvement)
    cgpa_res = res["counterfactual_outcomes"]["cgpa"]
    assert cgpa_res["delta"] > 0
    assert cgpa_res["ci_95"][0] < cgpa_res["ci_95"][1]

    # Verify presence of assumptions and disclaimer
    assert len(res["causal_assumptions"]) >= 3
    assert "medical_disclaimer" in res


def test_subgroup_analysis_structure(causal_dataset):
    """Verify subgroup heterogeneity analysis computes partitioned estimates."""
    analyze_subgroup_causal_effects = _get_subgroups()
    sub_effects = analyze_subgroup_causal_effects(causal_dataset)
    assert "by_gender" in sub_effects
    assert "Female" in sub_effects["by_gender"]
    assert "Male" in sub_effects["by_gender"]
    assert "by_age_group" in sub_effects
    assert "by_study_year" in sub_effects

    # Female sleep effect should be negative and close to -1.50
    female_sleep = sub_effects["by_gender"]["Female"]["sleep_hours -> depression_score"]["estimate"]
    assert -1.75 <= female_sleep <= -1.25
