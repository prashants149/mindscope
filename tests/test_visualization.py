"""
Unit Tests for Visualization & EDA Modules (Phase 8).
Validates EDA figure generation pipeline and output structures.
"""

from pathlib import Path
import pandas as pd
import pytest
from src.visualization.eda import generate_eda_reports


def test_eda_generation_pipeline(tmp_path):
    """Test that EDA pipeline generates figures and quantitative metrics."""
    # Synthetic mini-sample
    data = {
        "sleep_hours": [6.5, 7.0, 5.0, 8.0, 6.0],
        "screen_time_hours": [4.0, 5.5, 7.0, 3.5, 6.0],
        "academic_pressure": [3.0, 4.0, 5.0, 2.0, 3.0],
        "attendance_rate": [88.0, 92.0, 75.0, 95.0, 80.0],
        "cgpa": [7.8, 8.2, 6.5, 8.9, 7.2],
        "depression": [0, 0, 1, 0, 1],
        "depression_score": [8.0, 6.0, 18.0, 4.0, 15.0],
        "anxiety_score": [7.0, 5.0, 16.0, 5.0, 14.0],
        "social_support": [4.0, 4.5, 2.0, 4.0, 2.5],
        "financial_stress": [2.0, 1.5, 4.5, 2.0, 3.5],
        "physical_activity_hours": [3.0, 4.0, 1.0, 5.0, 2.0],
    }
    df = pd.DataFrame(data)
    stats = generate_eda_reports(df, tmp_path)

    assert isinstance(stats, dict)
    assert "dataset_rows" in stats
    assert stats["dataset_rows"] == 5

    # Check generated figure files
    expected_figures = [
        "eda_distribution_overview.png",
        "eda_correlation_matrix.png",
        "eda_bivariate_relationships.png",
        "eda_downstream_impacts.png",
    ]
    for fig_name in expected_figures:
        fig_path = tmp_path / fig_name
        assert fig_path.exists(), f"Expected figure {fig_name} was not created."
        assert fig_path.stat().st_size > 0
