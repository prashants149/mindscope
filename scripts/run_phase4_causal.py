"""
Executable runner for Phase 4: Causal Inference Engine.
Estimates causal effects with DoWhy & EconML, runs refutations, evaluates subgroup effects,
validates against synthetic ground truth, and tests counterfactual What-If queries.
"""

import json
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from src.causal.estimator import evaluate_all_causal_benchmarks
from src.causal.subgroups import analyze_subgroup_causal_effects
from src.causal.whatif import simulate_what_if_intervention


def main():
    print("=" * 65)
    print("MindScope Phase 4: Structural Causal Analysis & What-If Engine")
    print("=" * 65)

    data_path = PROJECT_ROOT / "data" / "processed" / "students_clean.csv"
    reports_dir = PROJECT_ROOT / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load Data
    print(f"\n[Step 1] Loading processed benchmark dataset from {data_path}...")
    df = pd.read_csv(data_path)

    # 2. Run Causal Estimation & Ground Truth Recovery Validation
    print("\n[Step 2] Estimating Causal Effects and Refutation Tests (DoWhy & EconML)...")
    causal_benchmarks = evaluate_all_causal_benchmarks(df)

    print("\n--- Causal Ground Truth Recovery Summary ---")
    for path, res in causal_benchmarks["path_evaluations"].items():
        status = "PASSED" if res["within_tolerance"] else "FAILED"
        print(
            f"  {path:<38}: Truth={res['ground_truth']:>6.2f} | "
            f"DoWhy={res['dowhy_estimate']:>6.2f} | "
            f"EconML={res['econml_estimate']:>6.2f} | "
            f"Err={res['absolute_error']:>5.3f} (Tol={res['tolerance']:>4.2f}) -> {status}"
        )

    # 3. Subgroup Heterogeneity Analysis
    print("\n[Step 3] Analyzing Subgroup Treatment Effects (Gender, Age, Study Year)...")
    subgroup_effects = analyze_subgroup_causal_effects(df)
    print("  -> Subgroup estimation completed across all demographic slices.")

    # 4. What-If Counterfactual Intervention Simulations
    print("\n[Step 4] Simulating Counterfactual What-If Interventions...")
    test_profile = {
        "student_id": "STU_SAMPLE_01",
        "depression_score": 14.5,
        "attendance_rate": 82.0,
        "cgpa": 7.4,
    }
    
    intervention_scenario = {
        "sleep_hours": 1.5,           # Increase sleep by 1.5 hours
        "academic_pressure": -1.0,     # Reduce academic pressure by 1 unit
        "screen_time_hours": -2.0,     # Reduce recreational screen time by 2 hours
    }

    whatif_result = simulate_what_if_intervention(test_profile, intervention_scenario)
    print("\n--- Counterfactual Intervention Scenario ---")
    print(f"  Applied Changes: {whatif_result['interventions_applied']}")
    print(f"  Narrative: {whatif_result['plain_english_narrative']}")
    print(f"  Depression Shift: {whatif_result['counterfactual_outcomes']['depression_score']['delta']} pts "
          f"(95% CI: {whatif_result['counterfactual_outcomes']['depression_score']['ci_95']})")
    print(f"  Attendance Shift: {whatif_result['counterfactual_outcomes']['attendance_rate']['delta']}% "
          f"(95% CI: {whatif_result['counterfactual_outcomes']['attendance_rate']['ci_95']})")
    print(f"  CGPA Shift: {whatif_result['counterfactual_outcomes']['cgpa']['delta']} pts "
          f"(95% CI: {whatif_result['counterfactual_outcomes']['cgpa']['ci_95']})")

    # 5. Export Consolidated Phase 4 Results
    combined_report = {
        "ground_truth_recovery": causal_benchmarks,
        "subgroup_heterogeneity": subgroup_effects,
        "what_if_simulation_example": whatif_result,
        "causal_assumptions": [
            "Consistency and Well-defined Interventions",
            "Conditional Exchangeability / Unconfoundedness given DAG backdoor adjustment set",
            "Positivity / Overlap across support of treatments and confounders",
            "Stable Unit Treatment Value Assumption (SUTVA)",
        ],
    }

    out_file = reports_dir / "causal_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(
            combined_report,
            f,
            indent=2,
            default=lambda obj: bool(obj) if isinstance(obj, (np.bool_, bool)) else float(obj) if isinstance(obj, (np.floating, float, np.integer, int)) else str(obj),
        )

    print(f"\n-> Full causal inference report exported to: {out_file}")
    print("\n" + "=" * 65)
    print("Phase 4 Causal Inference Completed Successfully.")
    print("=" * 65)


if __name__ == "__main__":
    main()
