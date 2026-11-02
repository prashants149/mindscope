"""
Training and evaluation pipeline for MindScope predictive models.
Integrates Stratified K-Fold CV, Class Imbalance weighting, Probability Calibration,
and MLflow tracking.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

# Ensure mindscope project root is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.metrics import (
    roc_auc_score,
    f1_score,
    recall_score,
    precision_score,
    brier_score_loss,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold, train_test_split

import mlflow
import mlflow.sklearn

from src.models.pipeline import (
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
    TARGET_COLUMN,
    get_model_specs,
    wrap_with_calibration,
)
from src.utils.constants import RANDOM_SEED


def train_and_evaluate_all(
    data_path: Path,
    output_dir: Path,
    reports_fig_dir: Path,
    mlflow_tracking_dir: Path,
) -> Dict[str, Any]:
    """
    Execute 5-fold Stratified CV, test evaluation, calibration assessment, and MLflow logging.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    reports_fig_dir.mkdir(parents=True, exist_ok=True)
    mlflow_tracking_dir.mkdir(parents=True, exist_ok=True)

    # Configure MLflow SQLite database tracking backend
    os.environ["MLFLOW_DISABLE_AGENT_HINT"] = "1"
    db_file = (mlflow_tracking_dir / "mlflow.db").resolve()
    mlflow_uri = f"sqlite:///{db_file.as_posix()}"
    mlflow.set_tracking_uri(mlflow_uri)
    mlflow.set_experiment("MindScope_Depression_Prediction")

    # Load data
    df = pd.read_csv(data_path)
    feature_cols = NUMERICAL_FEATURES + CATEGORICAL_FEATURES
    X = df[feature_cols].copy()
    y = df[TARGET_COLUMN].values

    # Train / Holdout Test Split (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=RANDOM_SEED, stratify=y
    )

    n_pos = int(y_train.sum())
    n_neg = len(y_train) - n_pos
    scale_pos_weight = n_neg / max(1, n_pos)

    base_models = get_model_specs(scale_pos_weight=scale_pos_weight)

    results: Dict[str, Any] = {
        "dataset_info": {
            "total_samples": len(df),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "positive_prevalence_train": float(y_train.mean()),
            "positive_prevalence_test": float(y_test.mean()),
        },
        "models": {},
    }

    # 5-Fold Stratified Cross-Validation on Training set
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_SEED)

    fig_roc, ax_roc = plt.subplots(figsize=(8, 6))
    fig_cal, ax_cal = plt.subplots(figsize=(8, 6))
    ax_cal.plot([0, 1], [0, 1], "k--", label="Perfect Calibration")

    best_test_auc = -1.0
    best_model_name = None
    best_model_obj = None

    for model_name, pipeline in base_models.items():
        print(f"\n--- Training & Cross-Validating: {model_name} ---")
        
        cv_metrics = {
            "roc_auc": [],
            "f1": [],
            "recall": [],
            "precision": [],
            "brier_score": [],
        }
        calibrated_cv_metrics = {
            "roc_auc": [],
            "f1": [],
            "recall": [],
            "precision": [],
            "brier_score": [],
        }

        for fold, (train_idx, val_idx) in enumerate(skf.split(X_train, y_train)):
            X_tr, y_tr = X_train.iloc[train_idx], y_train[train_idx]
            X_va, y_va = X_train.iloc[val_idx], y_train[val_idx]

            # Fit Base Model
            pipeline.fit(X_tr, y_tr)
            probs = pipeline.predict_proba(X_va)[:, 1]
            preds = (probs >= 0.5).astype(int)

            cv_metrics["roc_auc"].append(roc_auc_score(y_va, probs))
            cv_metrics["f1"].append(f1_score(y_va, preds))
            cv_metrics["recall"].append(recall_score(y_va, preds))
            cv_metrics["precision"].append(precision_score(y_va, preds))
            cv_metrics["brier_score"].append(brier_score_loss(y_va, probs))

            # Fit Calibrated Model (Sigmoid / Platt scaling via 3-fold inner calibration)
            calibrated_model = wrap_with_calibration(pipeline, cv=3, method="sigmoid")
            calibrated_model.fit(X_tr, y_tr)
            c_probs = calibrated_model.predict_proba(X_va)[:, 1]
            c_preds = (c_probs >= 0.5).astype(int)

            calibrated_cv_metrics["roc_auc"].append(roc_auc_score(y_va, c_probs))
            calibrated_cv_metrics["f1"].append(f1_score(y_va, c_preds))
            calibrated_cv_metrics["recall"].append(recall_score(y_va, c_preds))
            calibrated_cv_metrics["precision"].append(precision_score(y_va, c_preds))
            calibrated_cv_metrics["brier_score"].append(brier_score_loss(y_va, c_probs))

        # Train Final Models on full training set
        pipeline.fit(X_train, y_train)
        test_probs_raw = pipeline.predict_proba(X_test)[:, 1]
        test_preds_raw = (test_probs_raw >= 0.5).astype(int)

        calibrated_final = wrap_with_calibration(pipeline, cv=3, method="sigmoid")
        calibrated_final.fit(X_train, y_train)
        test_probs_cal = calibrated_final.predict_proba(X_test)[:, 1]
        test_preds_cal = (test_probs_cal >= 0.5).astype(int)

        # Compute holdout test metrics
        test_auc = float(roc_auc_score(y_test, test_probs_cal))
        test_f1 = float(f1_score(y_test, test_preds_cal))
        test_recall = float(recall_score(y_test, test_preds_cal))
        test_precision = float(precision_score(y_test, test_preds_cal))
        test_brier_raw = float(brier_score_loss(y_test, test_probs_raw))
        test_brier_cal = float(brier_score_loss(y_test, test_probs_cal))

        # Plot ROC curve for test set
        fpr, tpr, _ = roc_curve(y_test, test_probs_cal)
        ax_roc.plot(fpr, tpr, label=f"{model_name} (AUC = {test_auc:.3f})")

        # Plot Calibration curve
        prob_true, prob_pred = calibration_curve(y_test, test_probs_cal, n_bins=10)
        ax_cal.plot(prob_pred, prob_true, marker="o", label=f"{model_name} (Brier={test_brier_cal:.4f})")

        model_summary = {
            "cv_5fold": {
                "roc_auc_mean": round(float(np.mean(calibrated_cv_metrics["roc_auc"])), 4),
                "roc_auc_std": round(float(np.std(calibrated_cv_metrics["roc_auc"])), 4),
                "f1_mean": round(float(np.mean(calibrated_cv_metrics["f1"])), 4),
                "f1_std": round(float(np.std(calibrated_cv_metrics["f1"])), 4),
                "recall_mean": round(float(np.mean(calibrated_cv_metrics["recall"])), 4),
                "recall_std": round(float(np.std(calibrated_cv_metrics["recall"])), 4),
                "precision_mean": round(float(np.mean(calibrated_cv_metrics["precision"])), 4),
                "brier_score_mean": round(float(np.mean(calibrated_cv_metrics["brier_score"])), 4),
            },
            "holdout_test": {
                "roc_auc": round(test_auc, 4),
                "f1": round(test_f1, 4),
                "recall": round(test_recall, 4),
                "precision": round(test_precision, 4),
                "brier_score_uncalibrated": round(test_brier_raw, 4),
                "brier_score_calibrated": round(test_brier_cal, 4),
                "calibration_improvement_pct": round(
                    ((test_brier_raw - test_brier_cal) / max(1e-6, test_brier_raw)) * 100.0, 2
                ),
            },
        }

        results["models"][model_name] = model_summary

        # MLflow Run Logging
        with mlflow.start_run(run_name=f"{model_name}_Calibrated"):
            mlflow.log_param("model_type", model_name)
            mlflow.log_param("calibrated", True)
            mlflow.log_param("calibration_method", "sigmoid")
            mlflow.log_param("cv_folds", 5)
            mlflow.log_param("train_samples", len(X_train))
            mlflow.log_param("test_samples", len(X_test))

            # Log CV Metrics
            for metric, vals in calibrated_cv_metrics.items():
                mlflow.log_metric(f"cv_{metric}_mean", float(np.mean(vals)))
                mlflow.log_metric(f"cv_{metric}_std", float(np.std(vals)))

            # Log Test Metrics
            mlflow.log_metric("test_roc_auc", test_auc)
            mlflow.log_metric("test_f1", test_f1)
            mlflow.log_metric("test_recall", test_recall)
            mlflow.log_metric("test_precision", test_precision)
            mlflow.log_metric("test_brier_score", test_brier_cal)

            # Log model with cloudpickle serialization format
            mlflow.sklearn.log_model(
                calibrated_final,
                name="model",
                serialization_format="cloudpickle",
            )

        # Track best model
        if test_auc > best_test_auc:
            best_test_auc = test_auc
            best_model_name = model_name
            best_model_obj = calibrated_final

    # Finalize ROC curve plot
    ax_roc.plot([0, 1], [0, 1], "k--", label="Chance (AUC = 0.50)")
    ax_roc.set_title("ROC Curves Comparison on Holdout Test Set (N=600)")
    ax_roc.set_xlabel("False Positive Rate (1 - Specificity)")
    ax_roc.set_ylabel("True Positive Rate (Recall / Sensitivity)")
    ax_roc.legend(loc="lower right")
    fig_roc_path = reports_fig_dir / "model_roc_curves.png"
    fig_roc.tight_layout()
    fig_roc.savefig(fig_roc_path, dpi=300)
    plt.close(fig_roc)

    # Finalize Calibration curve plot
    ax_cal.set_title("Reliability Calibration Curves (Holdout Test Set)")
    ax_cal.set_xlabel("Mean Predicted Risk Probability")
    ax_cal.set_ylabel("Fraction of Observed Positives")
    ax_cal.legend(loc="upper left")
    fig_cal_path = reports_fig_dir / "model_calibration_curves.png"
    fig_cal.tight_layout()
    fig_cal.savefig(fig_cal_path, dpi=300)
    plt.close(fig_cal)

    # Save Best Model Artifact
    best_model_path = output_dir / "best_depression_classifier.joblib"
    joblib.dump(best_model_obj, best_model_path)
    results["best_model"] = {
        "name": best_model_name,
        "test_roc_auc": round(best_test_auc, 4),
        "artifact_path": str(best_model_path),
    }

    print("\n" + "=" * 60)
    print(f"Top Performing Model: {best_model_name} (ROC-AUC = {best_test_auc:.4f})")
    print(f"Artifact serialized to: {best_model_path}")
    print("=" * 60)

    return results
