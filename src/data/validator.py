"""
Data Validation Pipeline and Schema Enforcement for MindScope.
Includes Pydantic model for record validation and dataset-level sanity checks.
"""

from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from pydantic import BaseModel, Field, field_validator


class StudentRecordSchema(BaseModel):
    """Pydantic schema enforcing constraints on a single youth student record."""
    student_id: Optional[str] = Field(default=None, description="Unique anonymized student identifier")
    age: int = Field(ge=15, le=25, description="Youth age group 15-25")
    gender: str = Field(description="Gender identifier (Male, Female, Non-Binary, Unknown)")
    study_year: int = Field(ge=1, le=4, description="Year of undergraduate study (1-4)")
    sleep_hours: float = Field(ge=2.0, le=14.0, description="Average sleep per night in hours")
    screen_time_hours: float = Field(ge=0.5, le=16.0, description="Daily recreational screen time in hours")
    academic_pressure: int = Field(ge=1, le=5, description="Perceived academic pressure (1-5 Likert)")
    social_support: int = Field(ge=1, le=5, description="Perceived social support network (1-5 Likert)")
    financial_stress: int = Field(ge=1, le=5, description="Perceived financial burden (1-5 Likert)")
    physical_activity_hours: Optional[float] = Field(default=3.0, ge=0.0, le=21.0)
    anxiety_score: Optional[float] = Field(default=None, ge=0.0, le=21.0, description="GAD-7 anxiety scale")
    anxiety: Optional[int] = Field(default=None, ge=0, le=1)
    depression_score: Optional[float] = Field(default=None, ge=0.0, le=27.0, description="PHQ-9 depression scale")
    depression: Optional[int] = Field(default=None, ge=0, le=1, description="Binary depression indicator (score >= 10)")
    attendance_rate: float = Field(ge=0.0, le=100.0, description="Semester class attendance percentage")
    cgpa: float = Field(ge=0.0, le=10.0, description="Cumulative Grade Point Average (10.0 scale)")

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        valid_genders = {"Male", "Female", "Non-Binary", "Unknown"}
        if v not in valid_genders:
            raise ValueError(f"Gender must be one of {valid_genders}, got '{v}'")
        return v


def validate_student_dataset(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate a complete student dataset against research and clinical scale requirements.

    Returns:
        Structured dictionary with validation status, errors, warnings, and summary metrics.
    """
    errors: List[str] = []
    warnings: List[str] = []

    required_columns = [
        "age",
        "gender",
        "sleep_hours",
        "screen_time_hours",
        "academic_pressure",
        "social_support",
        "financial_stress",
        "attendance_rate",
        "cgpa",
    ]

    for col in required_columns:
        if col not in df.columns:
            errors.append(f"Missing mandatory column: '{col}'")

    if errors:
        return {
            "is_valid": False,
            "total_records": len(df),
            "errors": errors,
            "warnings": warnings,
            "metrics": {},
        }

    # Range and bounds validation
    if (df["age"] < 15).any() or (df["age"] > 25).any():
        errors.append("Age values detected outside the target 15-25 youth range.")

    if (df["attendance_rate"] < 0.0).any() or (df["attendance_rate"] > 100.0).any():
        errors.append("Attendance rate contains values outside [0.0, 100.0]%.")

    if (df["cgpa"] < 0.0).any() or (df["cgpa"] > 10.0).any():
        errors.append("CGPA values detected outside valid 0.0-10.0 range.")

    if (df["academic_pressure"] < 1).any() or (df["academic_pressure"] > 5).any():
        errors.append("academic_pressure contains values outside Likert range 1-5.")

    if (df["social_support"] < 1).any() or (df["social_support"] > 5).any():
        errors.append("social_support contains values outside Likert range 1-5.")

    if (df["financial_stress"] < 1).any() or (df["financial_stress"] > 5).any():
        errors.append("financial_stress contains values outside Likert range 1-5.")

    # Missing value checks
    null_counts = df[required_columns].isnull().sum()
    cols_with_nulls = null_counts[null_counts > 0].to_dict()
    if cols_with_nulls:
        errors.append(f"Null values present in required columns: {cols_with_nulls}")

    # Scale checks for depression
    if "depression_score" in df.columns:
        if (df["depression_score"] < 0.0).any() or (df["depression_score"] > 27.0).any():
            errors.append("depression_score values detected outside PHQ-9 range [0.0, 27.0].")

    # Degeneracy / variance checks
    for col in ["sleep_hours", "attendance_rate", "cgpa"]:
        std_val = df[col].std()
        if std_val == 0 or np.isnan(std_val):
            warnings.append(f"Column '{col}' has zero or undefined variance.")

    # Calculate summary metrics
    metrics = {
        "record_count": int(len(df)),
        "age_range": [int(df["age"].min()), int(df["age"].max())],
        "gender_distribution": df["gender"].value_counts(normalize=True).round(3).to_dict() if "gender" in df.columns else {},
        "mean_sleep_hours": round(float(df["sleep_hours"].mean()), 2),
        "mean_attendance": round(float(df["attendance_rate"].mean()), 2),
        "mean_cgpa": round(float(df["cgpa"].mean()), 2),
    }

    if "depression" in df.columns:
        metrics["depression_rate"] = round(float(df["depression"].mean()), 3)

    is_valid = len(errors) == 0
    return {
        "is_valid": is_valid,
        "total_records": len(df),
        "errors": errors,
        "warnings": warnings,
        "metrics": metrics,
    }
