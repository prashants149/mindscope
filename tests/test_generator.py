"""
Unit tests for the synthetic data generator and Structural Causal Model (SCM).
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
from src.data.generator import generate_synthetic_dataset, GROUND_TRUTH_EFFECTS


def test_generator_reproducibility():
    """Verify that fixing the random seed produces identical datasets."""
    df1, _ = generate_synthetic_dataset(n_samples=200, random_seed=42)
    df2, _ = generate_synthetic_dataset(n_samples=200, random_seed=42)
    pd.testing.assert_frame_equal(df1, df2)


def test_generator_bounds_and_types():
    """Verify generated columns respect specified boundaries."""
    df, meta = generate_synthetic_dataset(n_samples=500, random_seed=42)
    
    assert len(df) == 500
    assert df["age"].min() >= 15
    assert df["age"].max() <= 25
    assert set(df["gender"].unique()).issubset({"Male", "Female", "Non-Binary"})
    
    # Likert scales
    for col in ["academic_pressure", "social_support", "financial_stress"]:
        assert df[col].min() >= 1
        assert df[col].max() <= 5
        assert np.issubdtype(df[col].dtype, np.integer)
        
    # Standard clinical scales
    assert df["depression_score"].min() >= 0.0
    assert df["depression_score"].max() <= 27.0
    assert df["anxiety_score"].min() >= 0.0
    assert df["anxiety_score"].max() <= 21.0
    
    # Downstream metrics
    assert df["attendance_rate"].min() >= 0.0
    assert df["attendance_rate"].max() <= 100.0
    assert df["cgpa"].min() >= 0.0
    assert df["cgpa"].max() <= 10.0


def test_causal_correlations_direction():
    """Check that directional correlations match the SCM theoretical signs."""
    df, _ = generate_synthetic_dataset(n_samples=2000, random_seed=42)
    
    # Sleep should negatively correlate with depression
    corr_sleep_dep = df["sleep_hours"].corr(df["depression_score"])
    assert corr_sleep_dep < -0.20, f"Expected negative correlation, got {corr_sleep_dep}"
    
    # Academic pressure should positively correlate with depression
    corr_acad_dep = df["academic_pressure"].corr(df["depression_score"])
    assert corr_acad_dep > 0.30, f"Expected positive correlation, got {corr_acad_dep}"
    
    # Depression should negatively correlate with attendance
    corr_dep_att = df["depression_score"].corr(df["attendance_rate"])
    assert corr_dep_att < -0.40, f"Expected negative correlation, got {corr_dep_att}"
    
    # Depression should negatively correlate with CGPA
    corr_dep_cgpa = df["depression_score"].corr(df["cgpa"])
    assert corr_dep_cgpa < -0.30, f"Expected negative correlation, got {corr_dep_cgpa}"


def test_ground_truth_specification_structure():
    """Ensure metadata contains complete structural parameter definitions."""
    _, meta = generate_synthetic_dataset(n_samples=50, random_seed=42)
    gt = meta["ground_truth"]
    
    assert "direct_effects" in gt
    assert "total_effects" in gt
    assert "sleep_hours -> depression_score" in gt["direct_effects"]
    assert "academic_pressure -> depression_score" in gt["direct_effects"]
    assert "depression_score -> attendance_rate" in gt["direct_effects"]
    assert "depression_score -> cgpa" in gt["direct_effects"]
    
    # Numerical validation of specification
    assert gt["direct_effects"]["sleep_hours -> depression_score"] == -1.50
    assert gt["direct_effects"]["academic_pressure -> depression_score"] == 2.20
