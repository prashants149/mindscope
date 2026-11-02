"""
Executable runner for Phase 2: EDA, Calibrated Model Training, Cross-Validation,
and MLflow Tracking.
"""

import json
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from src.visualization.eda import generate_eda_reports
from src.models.train import train_and_evaluate_all


def main():
    print("=" * 65)
    print("MindScope Phase 2: EDA & Calibrated Predictive Modeling")
    print("=" * 65)

    data_path = PROJECT_ROOT / "data" / "processed" / "students_clean.csv"
    reports_fig_dir = PROJECT_ROOT / "reports" / "figures"
    reports_dir = PROJECT_ROOT / "reports"
    models_dir = PROJECT_ROOT / "models"
    mlruns_dir = PROJECT_ROOT / "mlruns"

    reports_fig_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    models_dir.mkdir(parents=True, exist_ok=True)

    # 1. Run EDA
    print("\n[Step 1] Executing Exploratory Data Analysis (EDA)...")
    df = pd.read_csv(data_path)
    eda_stats = generate_eda_reports(df, reports_fig_dir)
    eda_json_path = reports_dir / "eda_summary.json"
    with open(eda_json_path, "w", encoding="utf-8") as f:
        json.dump(eda_stats, f, indent=2)
    print(f"-> EDA figures generated at: {reports_fig_dir}")
    print(f"-> EDA summary saved to: {eda_json_path}")

    # 2. Run Modeling & Cross-Validation with Calibration & MLflow
    print("\n[Step 2] Training & Evaluating Predictive Models with MLflow...")
    model_results = train_and_evaluate_all(
        data_path=data_path,
        output_dir=models_dir,
        reports_fig_dir=reports_fig_dir,
        mlflow_tracking_dir=mlruns_dir,
    )

    metrics_path = reports_dir / "metrics_phase2.json"
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(model_results, f, indent=2)
    print(f"\n-> Complete Phase 2 metrics exported to: {metrics_path}")

    print("\n" + "=" * 65)
    print("Phase 2 Execution Completed Successfully.")
    print("=" * 65)


if __name__ == "__main__":
    main()
