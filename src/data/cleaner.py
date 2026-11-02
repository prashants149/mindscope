"""
Data Cleaning and Preprocessing Pipeline for Youth Mental Health Records.
Standardizes schemas, handles missing values, removes or imputes anomalies,
and enforces data integrity.
"""

from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd


def clean_student_data(
    df_raw: pd.DataFrame,
    drop_threshold_missing: float = 0.40,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Clean and standardize student mental health dataset.

    Args:
        df_raw: Input pandas DataFrame.
        drop_threshold_missing: Maximum fraction of missing fields allowed per row before dropping.

    Returns:
        Tuple of (clean_df, cleaning_report).
    """
    df = df_raw.copy()
    initial_rows = len(df)
    report: Dict[str, Any] = {
        "initial_rows": initial_rows,
        "dropped_rows": 0,
        "imputed_cells": {},
        "clipped_cells": {},
        "final_rows": 0,
    }

    # 1. Standardize column names (lowercase, underscores, remove punctuation)
    df.columns = [
        col.strip().lower().replace(" ", "_").replace("-", "_").replace("/", "_")
        for col in df.columns
    ]

    # Map alternative column names if coming from different survey sources
    column_aliases = {
        "cgpa_scale_10": "cgpa",
        "current_cgpa": "cgpa",
        "gpa": "cgpa",
        "study_hours": "screen_time_hours",
        "sleep_duration": "sleep_hours",
        "attendance": "attendance_rate",
        "financial_problems": "financial_stress",
        "academic_stress": "academic_pressure",
    }
    df = df.rename(columns=column_aliases)

    # 2. Drop rows with excessive missing data
    missing_ratio = df.isnull().mean(axis=1)
    to_drop = missing_ratio > drop_threshold_missing
    n_dropped = int(to_drop.sum())
    report["dropped_rows"] = n_dropped
    df = df.loc[~to_drop].copy().reset_index(drop=True)

    # 3. Clean Gender categories
    if "gender" in df.columns:
        def standardize_gender(val: Any) -> str:
            if pd.isna(val):
                return "Unknown"
            s = str(val).strip().lower()
            if s in ["m", "male", "man", "boy"]:
                return "Male"
            elif s in ["f", "female", "woman", "girl"]:
                return "Female"
            elif s in ["non-binary", "nb", "other", "genderqueer", "trans"]:
                return "Non-Binary"
            return "Unknown"

        df["gender"] = df["gender"].apply(standardize_gender)

    # 4. Clean and clip continuous & ordinal fields with boundaries
    numeric_specs = {
        "age": {"min": 15.0, "max": 25.0, "is_int": True, "default_median": 20.0},
        "study_year": {"min": 1.0, "max": 4.0, "is_int": True, "default_median": 2.0},
        "sleep_hours": {"min": 2.0, "max": 14.0, "is_int": False, "default_median": 7.0},
        "screen_time_hours": {"min": 0.5, "max": 16.0, "is_int": False, "default_median": 5.5},
        "academic_pressure": {"min": 1.0, "max": 5.0, "is_int": True, "default_median": 3.0},
        "social_support": {"min": 1.0, "max": 5.0, "is_int": True, "default_median": 3.0},
        "financial_stress": {"min": 1.0, "max": 5.0, "is_int": True, "default_median": 3.0},
        "physical_activity_hours": {"min": 0.0, "max": 21.0, "is_int": False, "default_median": 3.0},
        "anxiety_score": {"min": 0.0, "max": 21.0, "is_int": False, "default_median": 8.0},
        "depression_score": {"min": 0.0, "max": 27.0, "is_int": False, "default_median": 10.0},
        "attendance_rate": {"min": 0.0, "max": 100.0, "is_int": False, "default_median": 85.0},
        "cgpa": {"min": 0.0, "max": 10.0, "is_int": False, "default_median": 7.5},
    }

    for col, spec in numeric_specs.items():
        if col in df.columns:
            # Convert to numeric, errors='coerce' turns invalid strings to NaN
            df[col] = pd.to_numeric(df[col], errors="coerce")
            
            # Count and record missing values before imputation
            num_missing = int(df[col].isnull().sum())
            if num_missing > 0:
                median_val = df[col].median()
                if pd.isna(median_val):
                    median_val = spec["default_median"]
                df[col] = df[col].fillna(median_val)
                report["imputed_cells"][col] = num_missing

            # Count and clip out-of-range values
            lower_violations = (df[col] < spec["min"]).sum()
            upper_violations = (df[col] > spec["max"]).sum()
            total_clipped = int(lower_violations + upper_violations)
            if total_clipped > 0:
                report["clipped_cells"][col] = total_clipped
                df[col] = df[col].clip(lower=spec["min"], upper=spec["max"])

            if spec["is_int"]:
                df[col] = df[col].round().astype(int)
            else:
                df[col] = df[col].round(2)

    # 5. Synchronize binary target indicators if scores exist
    if "depression_score" in df.columns:
        df["depression"] = (df["depression_score"] >= 10.0).astype(int)
    elif "depression" in df.columns:
        df["depression"] = pd.to_numeric(df["depression"], errors="coerce").fillna(0).astype(int)

    if "anxiety_score" in df.columns:
        df["anxiety"] = (df["anxiety_score"] >= 10.0).astype(int)
    elif "anxiety" in df.columns:
        df["anxiety"] = pd.to_numeric(df["anxiety"], errors="coerce").fillna(0).astype(int)

    # 6. Ensure student_id
    if "student_id" not in df.columns:
        df["student_id"] = [f"STU_{10001 + i}" for i in range(len(df))]

    report["final_rows"] = len(df)
    return df, report
