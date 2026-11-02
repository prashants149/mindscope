"""
Executable pipeline script to generate, clean, validate, and store the synthetic dataset.
Exports datasets to data/synthetic and data/processed with full metadata.
"""

import json
import sys
from pathlib import Path

# Ensure mindscope project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from src.utils.constants import RANDOM_SEED
from src.data.generator import generate_synthetic_dataset
from src.data.cleaner import clean_student_data
from src.data.validator import validate_student_dataset


def main():
    base_dir = Path(__file__).resolve().parent.parent
    data_synthetic_dir = base_dir / "data" / "synthetic"
    data_processed_dir = base_dir / "data" / "processed"
    data_synthetic_dir.mkdir(parents=True, exist_ok=True)
    data_processed_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("MindScope Phase 1: Synthetic Data Generation & Validation")
    print("=" * 60)

    # 1. Generate clean benchmark dataset (n=3000)
    print("\n[Step 1] Generating synthetic benchmark dataset (N=3000, seed=42)...")
    df_raw, metadata = generate_synthetic_dataset(n_samples=3000, random_seed=RANDOM_SEED, inject_anomalies=False)
    raw_path = data_synthetic_dir / "synthetic_students_raw.csv"
    df_raw.to_csv(raw_path, index=False)
    print(f"-> Saved raw synthetic dataset to: {raw_path}")

    # 2. Generate anomaly test dataset for cleaning pipeline verification
    print("\n[Step 2] Generating anomaly test dataset with injected noise...")
    df_noisy, _ = generate_synthetic_dataset(n_samples=1000, random_seed=RANDOM_SEED + 1, inject_anomalies=True)
    noisy_path = data_synthetic_dir / "synthetic_students_noisy_test.csv"
    df_noisy.to_csv(noisy_path, index=False)
    print(f"-> Saved noisy benchmark to: {noisy_path}")

    # 3. Clean datasets
    print("\n[Step 3] Running data cleaning pipeline on raw benchmark dataset...")
    df_clean, clean_report = clean_student_data(df_raw)
    clean_path = data_processed_dir / "students_clean.csv"
    df_clean.to_csv(clean_path, index=False)
    print(f"-> Clean report: {clean_report}")
    print(f"-> Saved processed clean dataset to: {clean_path}")

    # 4. Clean noisy test dataset to verify cleaning capability
    print("\n[Step 4] Running data cleaning pipeline on noisy dataset...")
    df_noisy_cleaned, noisy_clean_report = clean_student_data(df_noisy)
    print(f"-> Noisy data cleaned report: {noisy_clean_report}")

    # 5. Validate dataset
    print("\n[Step 5] Validating processed dataset...")
    validation_result = validate_student_dataset(df_clean)
    print(f"-> Validation passed: {validation_result['is_valid']}")
    print(f"-> Errors: {validation_result['errors']}")
    print(f"-> Warnings: {validation_result['warnings']}")
    print(f"-> Key Metrics: {json.dumps(validation_result['metrics'], indent=2)}")

    # 6. Save metadata and ground truth
    meta_path = data_synthetic_dir / "causal_ground_truth.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"\n-> Exported SCM ground-truth parameters to: {meta_path}")

    print("\n" + "=" * 60)
    print("Phase 1 Generation and Validation Pipeline Completed Successfully.")
    print("=" * 60)


if __name__ == "__main__":
    main()
