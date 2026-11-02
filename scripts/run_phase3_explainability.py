"""
Executable runner for Phase 3: Global and Local SHAP Explanations,
Visualizations, and Plain-English Factor Summaries with Causal Guardrails.
"""

import json
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import joblib
import pandas as pd
from src.explainability.explainer import MindScopeExplainer
from src.explainability.visualizer import generate_shap_visualizations


def main():
    print("=" * 65)
    print("MindScope Phase 3: Model Explainability & SHAP Attributions")
    print("=" * 65)

    data_path = PROJECT_ROOT / "data" / "processed" / "students_clean.csv"
    model_path = PROJECT_ROOT / "models" / "best_depression_classifier.joblib"
    reports_fig_dir = PROJECT_ROOT / "reports" / "figures"
    reports_dir = PROJECT_ROOT / "reports"

    reports_fig_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load Data and Model
    print(f"\n[Step 1] Loading processed dataset and calibrated classifier from {model_path}...")
    df = pd.read_csv(data_path)
    model = joblib.load(model_path)

    # 2. Initialize MindScopeExplainer
    print("\n[Step 2] Initializing SHAP Explainer with background dataset...")
    explainer = MindScopeExplainer(model_pipeline=model, background_df=df.sample(300, random_state=42))

    # 3. Global Feature Importance Ranking
    print("\n[Step 3] Computing Global SHAP Feature Importance Ranking...")
    eval_sample = df.sample(500, random_state=42)
    global_importance = explainer.get_global_importance(eval_sample)
    for rank, item in enumerate(global_importance, start=1):
        print(f"  {rank}. {item['display_name']:<32}: {item['mean_abs_shap']:.4f} |log-odds|")

    # 4. Generate Visualizations
    print("\n[Step 4] Generating publication-quality SHAP figures...")
    figures = generate_shap_visualizations(explainer, eval_sample, reports_fig_dir)
    for fig_p in figures:
        print(f"  -> Created: {fig_p}")

    # 5. Local Student Case Studies
    print("\n[Step 5] Computing Local Explanations on Canonical Student Profiles...")

    # Case A: High-Risk Profile (Severe academic and financial stress, sleep deprived)
    student_high = {
        "student_id": "STU_CASE_HIGH",
        "age": 21,
        "gender": "Female",
        "study_year": 3,
        "sleep_hours": 4.5,
        "screen_time_hours": 8.5,
        "academic_pressure": 5,
        "social_support": 1,
        "financial_stress": 5,
        "physical_activity_hours": 1.0,
    }
    exp_high = explainer.explain_single_student(student_high)
    print("\n[Case Study 1: High-Stress Profile]")
    print(f"  Risk Probability: {exp_high['predicted_risk_probability'] * 100:.1f}% ({exp_high['risk_tier']})")
    print(f"  Summary: {exp_high['plain_english_summary']}")
    print(f"  Guardrail: {exp_high['epistemic_guardrail']}")

    # Case B: Low-Risk Profile (High social support, good sleep, low stress)
    student_low = {
        "student_id": "STU_CASE_LOW",
        "age": 19,
        "gender": "Male",
        "study_year": 1,
        "sleep_hours": 8.5,
        "screen_time_hours": 3.0,
        "academic_pressure": 1,
        "social_support": 5,
        "financial_stress": 1,
        "physical_activity_hours": 6.0,
    }
    exp_low = explainer.explain_single_student(student_low)
    print("\n[Case Study 2: Resilient Profile]")
    print(f"  Risk Probability: {exp_low['predicted_risk_probability'] * 100:.1f}% ({exp_low['risk_tier']})")
    print(f"  Summary: {exp_low['plain_english_summary']}")

    # Case C: Ambiguous / Moderate Profile
    student_mod = {
        "student_id": "STU_CASE_MOD",
        "age": 20,
        "gender": "Non-Binary",
        "study_year": 2,
        "sleep_hours": 6.5,
        "screen_time_hours": 6.0,
        "academic_pressure": 3,
        "social_support": 3,
        "financial_stress": 3,
        "physical_activity_hours": 3.0,
    }
    exp_mod = explainer.explain_single_student(student_mod)

    # 6. Export Summary JSON
    summary_data = {
        "global_importance_ranking": global_importance,
        "case_studies": {
            "high_risk": exp_high,
            "resilient": exp_low,
            "moderate": exp_mod,
        },
        "figures_generated": figures,
    }
    summary_path = reports_dir / "shap_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)

    print(f"\n-> Complete Explainability Report exported to: {summary_path}")
    print("\n" + "=" * 65)
    print("Phase 3 Explainability Completed Successfully.")
    print("=" * 65)


if __name__ == "__main__":
    main()
