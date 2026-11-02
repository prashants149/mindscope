"""
Synthetic Data Generator with Known Structural Causal Model (SCM).

This generator implements a mathematically well-defined Directed Acyclic Graph (DAG)
connecting youth lifestyle and academic stressors to depression and downstream
academic outcomes (attendance and CGPA).

Causal Graph Structure:
  Exogenous / Root Variables:
    - Age (15-25)
    - Gender
    - Financial Stress (1-5)
    - Social Support (1-5)
    - Academic Pressure (1-5) [influenced by financial stress]
    - Screen Time (hours/day) [influenced by academic pressure & social support]
    - Sleep Duration (hours/day) [influenced by academic pressure & screen time]

  Primary Intermediate Mediator:
    - Depression Severity (continuous PHQ-9 scale 0-27) & binary indicator (>= 10)
      Causes: Sleep (-), Screen Time (+), Academic Pressure (+), Social Support (-), Financial Stress (+)

  Downstream Outcomes:
    - Attendance Rate (%) <- Depression (-), Sleep (+)
    - CGPA (0.0-10.0 scale) <- Depression (-), Academic Pressure (-)
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, Tuple
import numpy as np
import pandas as pd

from src.utils.constants import RANDOM_SEED


@dataclass(frozen=True)
class CausalGraphSpecification:
    """Ground truth causal structural coefficients."""
    # Direct effects on depression_score (PHQ-9 0-27)
    intercept_depression: float = 12.0
    beta_sleep_on_dep: float = -1.50         # 1 hr more sleep reduces depression by 1.5 pts
    beta_screen_on_dep: float = 0.80         # 1 hr more screen time increases depression by 0.8 pts
    beta_acad_on_dep: float = 2.20           # 1 unit increase in pressure adds 2.2 pts
    beta_support_on_dep: float = -1.80       # 1 unit increase in support reduces depression by 1.8 pts
    beta_fin_on_dep: float = 1.60            # 1 unit increase in financial stress adds 1.6 pts
    sigma_dep: float = 1.50

    # Direct effects on attendance_rate (0-100%)
    intercept_attendance: float = 92.0
    beta_dep_on_att: float = -0.80           # 1 pt higher depression reduces attendance by 0.80%
    beta_sleep_on_att: float = 1.20          # 1 hr more sleep directly improves attendance by 1.20%
    sigma_att: float = 3.0

    # Direct effects on cgpa (0.0-10.0 scale)
    intercept_cgpa: float = 8.80
    beta_dep_on_cgpa: float = -0.09          # 1 pt higher depression reduces CGPA by 0.09 pts
    beta_acad_on_cgpa: float = -0.15         # direct stress fatigue reduces CGPA by 0.15 pts
    sigma_cgpa: float = 0.40

    # Direct effects on anxiety_score (GAD-7 scale 0-21)
    intercept_anxiety: float = 8.0
    beta_acad_on_anx: float = 1.90
    beta_screen_on_anx: float = 0.60
    beta_sleep_on_anx: float = -1.10
    beta_fin_on_anx: float = 1.20
    sigma_anx: float = 1.40


# Instantiate default ground truth parameters
GROUND_TRUTH_EFFECTS = CausalGraphSpecification()


def get_ground_truth_dict() -> Dict[str, Any]:
    """Return dictionary of theoretical ground truth direct and total causal effects."""
    gt = GROUND_TRUTH_EFFECTS
    
    # Analytical total effects through linear structural chain:
    # Total effect of Sleep on Attendance = beta_sleep_on_att + (beta_sleep_on_dep * beta_dep_on_att)
    total_sleep_on_att = gt.beta_sleep_on_att + (gt.beta_sleep_on_dep * gt.beta_dep_on_att)
    
    # Total effect of Academic Pressure on CGPA = beta_acad_on_cgpa + (beta_acad_on_dep * beta_dep_on_cgpa)
    total_acad_on_cgpa = gt.beta_acad_on_cgpa + (gt.beta_acad_on_dep * gt.beta_dep_on_cgpa)

    # Total effect of Sleep on CGPA = beta_sleep_on_dep * beta_dep_on_cgpa
    total_sleep_on_cgpa = gt.beta_sleep_on_dep * gt.beta_dep_on_cgpa

    return {
        "direct_effects": {
            "sleep_hours -> depression_score": gt.beta_sleep_on_dep,
            "screen_time_hours -> depression_score": gt.beta_screen_on_dep,
            "academic_pressure -> depression_score": gt.beta_acad_on_dep,
            "social_support -> depression_score": gt.beta_support_on_dep,
            "financial_stress -> depression_score": gt.beta_fin_on_dep,
            "depression_score -> attendance_rate": gt.beta_dep_on_att,
            "sleep_hours -> attendance_rate": gt.beta_sleep_on_att,
            "depression_score -> cgpa": gt.beta_dep_on_cgpa,
            "academic_pressure -> cgpa": gt.beta_acad_on_cgpa,
        },
        "total_effects": {
            "sleep_hours -> attendance_rate": total_sleep_on_att,
            "academic_pressure -> cgpa": total_acad_on_cgpa,
            "sleep_hours -> cgpa": total_sleep_on_cgpa,
        },
        "raw_specification": asdict(gt),
    }


def generate_synthetic_dataset(
    n_samples: int = 3000,
    random_seed: int = RANDOM_SEED,
    inject_anomalies: bool = False,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Generate synthetic youth mental health dataset using the SCM.

    Args:
        n_samples: Number of student profiles to generate.
        random_seed: Seed for NumPy PRNG for strict reproducibility.
        inject_anomalies: If True, inject small percentage of noisy/dirty data
                          to test the cleaning and validation pipelines.

    Returns:
        Tuple of (DataFrame of students, dictionary of ground-truth effects & metadata).
    """
    rng = np.random.default_rng(random_seed)
    gt = GROUND_TRUTH_EFFECTS

    # 1. Demographics (Ages 15-25 as required by project scope)
    student_ids = [f"STU_{idx+10001}" for idx in range(n_samples)]
    age = rng.integers(low=15, high=26, size=n_samples)  # 15 to 25 inclusive
    gender = rng.choice(["Female", "Male", "Non-Binary"], size=n_samples, p=[0.49, 0.47, 0.04])
    study_year = rng.integers(low=1, high=5, size=n_samples)  # Years 1 to 4

    # 2. Exogenous Stressors and Support Networks (Likert 1 to 5)
    financial_stress = rng.choice([1, 2, 3, 4, 5], size=n_samples, p=[0.15, 0.25, 0.30, 0.20, 0.10])
    social_support = rng.choice([1, 2, 3, 4, 5], size=n_samples, p=[0.12, 0.23, 0.35, 0.20, 0.10])

    # Academic pressure (partially influenced by financial stress & study year)
    latent_acad = (
        2.5
        + 0.25 * (financial_stress - 3)
        + 0.15 * (study_year - 2.5)
        + rng.normal(0, 0.8, size=n_samples)
    )
    academic_pressure = np.clip(np.round(latent_acad), 1, 5).astype(int)

    # 3. Behavioral Factors: Screen time and Sleep
    # High academic pressure & lower social support increase recreational/escapist screen time
    latent_screen = (
        5.5
        + 0.40 * (academic_pressure - 3)
        - 0.35 * (social_support - 3)
        + rng.normal(0, 1.2, size=n_samples)
    )
    screen_time_hours = np.clip(np.round(latent_screen, 1), 1.0, 14.0)

    # Sleep hours reduced by academic pressure and screen time
    latent_sleep = (
        7.2
        - 0.35 * (academic_pressure - 3)
        - 0.25 * (screen_time_hours - 5.5)
        + rng.normal(0, 0.7, size=n_samples)
    )
    sleep_hours = np.clip(np.round(latent_sleep, 1), 3.0, 11.0)

    # Weekly physical activity (0-14 hours)
    physical_activity_hours = np.clip(
        np.round(rng.exponential(scale=3.0, size=n_samples), 1),
        0.0,
        14.0,
    )

    # 4. Latent Distress and Depression (Mediator)
    # PHQ-9 scale: 0 to 27 (>= 10 indicates moderate-to-severe depression)
    dep_noise = rng.normal(0, gt.sigma_dep, size=n_samples)
    continuous_dep = (
        gt.intercept_depression
        + gt.beta_sleep_on_dep * (sleep_hours - 7.0)
        + gt.beta_screen_on_dep * (screen_time_hours - 5.5)
        + gt.beta_acad_on_dep * (academic_pressure - 3.0)
        + gt.beta_support_on_dep * (social_support - 3.0)
        + gt.beta_fin_on_dep * (financial_stress - 3.0)
        + dep_noise
    )
    depression_score = np.clip(np.round(continuous_dep, 1), 0.0, 27.0)
    depression_binary = (depression_score >= 10.0).astype(int)

    # Anxiety score (GAD-7 scale: 0 to 21)
    anx_noise = rng.normal(0, gt.sigma_anx, size=n_samples)
    continuous_anx = (
        gt.intercept_anxiety
        + gt.beta_acad_on_anx * (academic_pressure - 3.0)
        + gt.beta_screen_on_anx * (screen_time_hours - 5.5)
        + gt.beta_sleep_on_anx * (sleep_hours - 7.0)
        + gt.beta_fin_on_anx * (financial_stress - 3.0)
        + anx_noise
    )
    anxiety_score = np.clip(np.round(continuous_anx, 1), 0.0, 21.0)
    anxiety_binary = (anxiety_score >= 10.0).astype(int)

    # 5. Downstream Academic Outcomes
    # Attendance Rate (%)
    att_noise = rng.normal(0, gt.sigma_att, size=n_samples)
    attendance_rate = (
        gt.intercept_attendance
        + gt.beta_dep_on_att * (depression_score - 10.0)
        + gt.beta_sleep_on_att * (sleep_hours - 7.0)
        + att_noise
    )
    attendance_rate = np.clip(np.round(attendance_rate, 1), 40.0, 100.0)

    # CGPA (10.0 scale)
    cgpa_noise = rng.normal(0, gt.sigma_cgpa, size=n_samples)
    cgpa = (
        gt.intercept_cgpa
        + gt.beta_dep_on_cgpa * (depression_score - 10.0)
        + gt.beta_acad_on_cgpa * (academic_pressure - 3.0)
        + cgpa_noise
    )
    cgpa = np.clip(np.round(cgpa, 2), 2.0, 10.0)

    df = pd.DataFrame({
        "student_id": student_ids,
        "age": age,
        "gender": gender,
        "study_year": study_year,
        "sleep_hours": sleep_hours,
        "screen_time_hours": screen_time_hours,
        "academic_pressure": academic_pressure,
        "social_support": social_support,
        "financial_stress": financial_stress,
        "physical_activity_hours": physical_activity_hours,
        "anxiety_score": anxiety_score,
        "anxiety": anxiety_binary,
        "depression_score": depression_score,
        "depression": depression_binary,
        "attendance_rate": attendance_rate,
        "cgpa": cgpa,
    })

    if inject_anomalies:
        # Inject realistic anomalies for data cleaning testing (e.g. 1.5% of rows)
        n_corrupt = max(5, int(n_samples * 0.015))
        corrupt_indices = rng.choice(n_samples, size=n_corrupt, replace=False)
        for i, idx in enumerate(corrupt_indices):
            if i % 5 == 0:
                df.loc[idx, "age"] = -1  # Negative age
            elif i % 5 == 1:
                df.loc[idx, "gender"] = "unknown_str"  # Inconsistent category
            elif i % 5 == 2:
                df.loc[idx, "cgpa"] = 15.5  # CGPA > 10.0
            elif i % 5 == 3:
                df.loc[idx, "sleep_hours"] = np.nan  # Missing value
            elif i % 5 == 4:
                df.loc[idx, "attendance_rate"] = 145.0  # Attendance > 100%

    metadata = {
        "n_samples": n_samples,
        "random_seed": random_seed,
        "ground_truth": get_ground_truth_dict(),
        "summary": {
            "depression_prevalence": float(df["depression"].mean()),
            "anxiety_prevalence": float(df["anxiety"].mean()),
            "mean_attendance": float(df["attendance_rate"].mean()),
            "mean_cgpa": float(df["cgpa"].mean()),
            "mean_sleep_hours": float(df["sleep_hours"].mean()),
            "mean_screen_time": float(df["screen_time_hours"].mean()),
        },
    }

    return df, metadata


if __name__ == "__main__":
    df, meta = generate_synthetic_dataset(n_samples=1000)
    print("Generated shape:", df.shape)
    print("Metadata ground truth direct effects:", meta["ground_truth"]["direct_effects"])
    print("Summary stats:", meta["summary"])
