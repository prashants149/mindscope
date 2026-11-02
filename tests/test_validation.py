"""
Unit tests for data cleaning and schema validation.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
import pandas as pd
from pydantic import ValidationError

from src.data.cleaner import clean_student_data
from src.data.validator import validate_student_dataset, StudentRecordSchema
from src.data.generator import generate_synthetic_dataset


def test_cleaner_handles_missing_and_outliers():
    """Test cleaner imputes missing cells and clips anomalous ranges."""
    dirty_data = pd.DataFrame([{
        "Student ID": "STU_9999",
        "Age": 28,  # Out of range (max 25)
        "Gender": "male",  # Non-standard case
        "Study Year": 3,
        "Sleep Hours": None,  # Missing
        "Screen Time Hours": 6.0,
        "Academic Pressure": 4,
        "Social Support": 3,
        "Financial Stress": 2,
        "Attendance Rate": 105.0,  # Out of range (> 100)
        "CGPA": -1.0,  # Negative
    }])
    
    clean_df, report = clean_student_data(dirty_data)
    
    assert len(clean_df) == 1
    assert clean_df.loc[0, "gender"] == "Male"
    assert clean_df.loc[0, "age"] == 25  # Clipped
    assert clean_df.loc[0, "attendance_rate"] == 100.0  # Clipped
    assert clean_df.loc[0, "cgpa"] == 0.0  # Clipped
    assert clean_df.loc[0, "sleep_hours"] == 7.0  # Imputed with default median
    assert report["imputed_cells"]["sleep_hours"] == 1
    assert "age" in report["clipped_cells"]


def test_cleaner_drops_excessively_empty_rows():
    """Verify that rows with >40% missing data are eliminated."""
    dirty_data = pd.DataFrame([
        {"age": 20, "gender": "Female", "cgpa": 8.0},  # Majority missing
        {"age": 21, "gender": "Male", "study_year": 3, "sleep_hours": 7.0,
         "screen_time_hours": 5.0, "academic_pressure": 3, "social_support": 3,
         "financial_stress": 3, "attendance_rate": 90.0, "cgpa": 8.5},
    ])
    clean_df, report = clean_student_data(dirty_data, drop_threshold_missing=0.40)
    assert len(clean_df) == 1
    assert report["dropped_rows"] == 1


def test_validator_on_clean_data():
    """Verify validator returns True on standard generated dataset."""
    df, _ = generate_synthetic_dataset(n_samples=200, random_seed=42)
    clean_df, _ = clean_student_data(df)
    res = validate_student_dataset(clean_df)
    assert res["is_valid"] is True
    assert len(res["errors"]) == 0
    assert res["total_records"] == 200


def test_validator_detects_violations():
    """Verify validator flags illegal ages, missing columns, and bad ranges."""
    # Missing column
    bad_df_1 = pd.DataFrame({"age": [20], "gender": ["Female"]})
    res_1 = validate_student_dataset(bad_df_1)
    assert res_1["is_valid"] is False
    assert any("Missing mandatory column" in err for err in res_1["errors"])

    # Age outside 15-25
    df_valid, _ = generate_synthetic_dataset(n_samples=50, random_seed=42)
    df_valid.loc[0, "age"] = 12
    res_2 = validate_student_dataset(df_valid)
    assert res_2["is_valid"] is False
    assert any("Age values detected outside" in err for err in res_2["errors"])


def test_pydantic_schema_enforcement():
    """Verify StudentRecordSchema validates good input and rejects violations."""
    valid_record = {
        "student_id": "STU_10001",
        "age": 20,
        "gender": "Female",
        "study_year": 2,
        "sleep_hours": 7.5,
        "screen_time_hours": 4.5,
        "academic_pressure": 3,
        "social_support": 4,
        "financial_stress": 2,
        "attendance_rate": 94.0,
        "cgpa": 8.8,
    }
    schema = StudentRecordSchema(**valid_record)
    assert schema.age == 20
    assert schema.gender == "Female"

    # Invalid age (under 15)
    invalid_record = valid_record.copy()
    invalid_record["age"] = 14
    with pytest.raises(ValidationError):
        StudentRecordSchema(**invalid_record)
