"""
Subgroup Causal Heterogeneity Analysis.
Estimates conditional treatment effects across Gender, Age Groups, and Academic Years.
"""

from typing import Dict, Any, List
import pandas as pd
from src.causal.estimator import run_single_causal_pipeline, BACKDOOR_CONFOUNDERS


def analyze_subgroup_causal_effects(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute causal effect estimates partitioned by demographic subgroups.
    """
    subgroup_results: Dict[str, Any] = {
        "by_gender": {},
        "by_age_group": {},
        "by_study_year": {},
    }

    key_paths = [
        "sleep_hours -> depression_score",
        "academic_pressure -> depression_score",
        "depression_score -> attendance_rate",
        "depression_score -> cgpa",
    ]

    # 1. By Gender
    for gender_val in ["Female", "Male"]:
        sub_df = df[df["gender"] == gender_val].copy()
        subgroup_results["by_gender"][gender_val] = {}
        for path in key_paths:
            treatment, outcome = path.split(" -> ")
            confounders = [c for c in BACKDOOR_CONFOUNDERS.get(path, ["age"]) if c != "gender"]
            res = run_single_causal_pipeline(
                sub_df, treatment, outcome, confounders, run_refutations=False
            )
            subgroup_results["by_gender"][gender_val][path] = {
                "estimate": res["dowhy_estimate"],
                "ci_95": res["dowhy_ci_95"],
            }

    # 2. By Age Group: 15-19 vs 20-25
    age_groups = {
        "15-19 (Younger Youth)": df[df["age"] <= 19],
        "20-25 (Older Youth)": df[df["age"] >= 20],
    }
    for grp_name, sub_df in age_groups.items():
        subgroup_results["by_age_group"][grp_name] = {}
        for path in key_paths:
            treatment, outcome = path.split(" -> ")
            confounders = [c for c in BACKDOOR_CONFOUNDERS.get(path, ["age"]) if c != "age"]
            res = run_single_causal_pipeline(
                sub_df, treatment, outcome, confounders, run_refutations=False
            )
            subgroup_results["by_age_group"][grp_name][path] = {
                "estimate": res["dowhy_estimate"],
                "ci_95": res["dowhy_ci_95"],
            }

    # 3. By Study Year: Years 1-2 vs Years 3-4
    year_groups = {
        "Years 1-2 (Underclassmen)": df[df["study_year"] <= 2],
        "Years 3-4 (Upperclassmen)": df[df["study_year"] >= 3],
    }
    for grp_name, sub_df in year_groups.items():
        subgroup_results["by_study_year"][grp_name] = {}
        for path in key_paths:
            treatment, outcome = path.split(" -> ")
            confounders = BACKDOOR_CONFOUNDERS.get(path, ["age"])
            res = run_single_causal_pipeline(
                sub_df, treatment, outcome, confounders, run_refutations=False
            )
            subgroup_results["by_study_year"][grp_name][path] = {
                "estimate": res["dowhy_estimate"],
                "ci_95": res["dowhy_ci_95"],
            }

    return subgroup_results
