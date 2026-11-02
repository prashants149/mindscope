"""
Algorithmic Fairness and Subgroup Auditing Engine for MindScope.
Evaluates demographic parity, equalized odds (recall parity & FPR parity),
and calibration across gender and age cohorts.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from sklearn.metrics import recall_score, roc_auc_score, brier_score_loss, confusion_matrix
import joblib

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.models.pipeline import NUMERICAL_FEATURES, CATEGORICAL_FEATURES, TARGET_COLUMN


def categorize_age_group(age: int) -> str:
    """Discretize continuous age into meaningful developmental cohorts."""
    if age <= 18:
        return "Adolescent (15-18)"
    elif age <= 21:
        return "Early Undergraduate (19-21)"
    else:
        return "Senior / Post-Grad (22-25)"


def run_fairness_audit(
    model_path: Optional[Path] = None,
    data_path: Optional[Path] = None,
    output_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """
    Perform comprehensive fairness audit across gender and age cohorts.
    """
    if model_path is None:
        model_path = PROJECT_ROOT / "models" / "best_depression_classifier.joblib"
    if data_path is None:
        data_path = PROJECT_ROOT / "data" / "processed" / "students_clean.csv"
    if output_path is None:
        output_path = PROJECT_ROOT / "reports" / "fairness_audit_results.json"

    # Load artifacts
    model = joblib.load(model_path)
    df = pd.read_csv(data_path)

    # Feature definitions
    feature_cols = NUMERICAL_FEATURES + CATEGORICAL_FEATURES
    target_col = TARGET_COLUMN

    y_true = df[target_col].values
    y_prob = model.predict_proba(df[feature_cols])[:, 1]
    y_pred = (y_prob >= 0.5).astype(int)

    df_eval = df.copy()
    df_eval["y_true"] = y_true
    df_eval["y_prob"] = y_prob
    df_eval["y_pred"] = y_pred
    df_eval["age_group"] = df_eval["age"].apply(categorize_age_group)

    audit_report: Dict[str, Any] = {
        "overall_sample_size": len(df_eval),
        "overall_metrics": {
            "prevalence": float(round(np.mean(y_true), 4)),
            "selection_rate": float(round(np.mean(y_pred), 4)),
            "recall": float(round(recall_score(y_true, y_pred), 4)),
            "roc_auc": float(round(roc_auc_score(y_true, y_prob), 4)),
            "brier_score": float(round(brier_score_loss(y_true, y_prob), 4)),
        },
        "gender_audit": {},
        "age_group_audit": {},
        "disparate_impact_analysis": {},
        "fairness_verdict": {},
    }

    # 1. Audit Gender Subgroups
    genders = sorted(df_eval["gender"].unique())
    gender_recalls = {}
    gender_selection_rates = {}

    for g in genders:
        sub = df_eval[df_eval["gender"] == g]
        yt = sub["y_true"].values
        yp = sub["y_pred"].values
        ypr = sub["y_prob"].values

        tn, fp, fn, tp = confusion_matrix(yt, yp, labels=[0, 1]).ravel()
        rec = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
        fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
        sel_rate = float(np.mean(yp))

        gender_recalls[g] = rec
        gender_selection_rates[g] = sel_rate

        audit_report["gender_audit"][g] = {
            "count": int(len(sub)),
            "prevalence": float(round(np.mean(yt), 4)),
            "selection_rate": float(round(sel_rate, 4)),
            "recall_tpr": float(round(rec, 4)),
            "false_positive_rate": float(round(fpr, 4)),
            "roc_auc": float(round(roc_auc_score(yt, ypr), 4)),
            "brier_score": float(round(brier_score_loss(yt, ypr), 4)),
        }

    # 2. Audit Age Cohorts
    age_groups = sorted(df_eval["age_group"].unique())
    age_recalls = {}
    age_selection_rates = {}

    for ag in age_groups:
        sub = df_eval[df_eval["age_group"] == ag]
        yt = sub["y_true"].values
        yp = sub["y_pred"].values
        ypr = sub["y_prob"].values

        tn, fp, fn, tp = confusion_matrix(yt, yp, labels=[0, 1]).ravel()
        rec = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
        fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
        sel_rate = float(np.mean(yp))

        age_recalls[ag] = rec
        age_selection_rates[ag] = sel_rate

        audit_report["age_group_audit"][ag] = {
            "count": int(len(sub)),
            "prevalence": float(round(np.mean(yt), 4)),
            "selection_rate": float(round(sel_rate, 4)),
            "recall_tpr": float(round(rec, 4)),
            "false_positive_rate": float(round(fpr, 4)),
            "roc_auc": float(round(roc_auc_score(yt, ypr), 4)),
            "brier_score": float(round(brier_score_loss(yt, ypr), 4)),
        }

    # 3. Disparate Impact & Parity Ratios (80% Rule)
    gender_di_ratio = min(gender_selection_rates.values()) / max(gender_selection_rates.values())
    gender_rec_ratio = min(gender_recalls.values()) / max(gender_recalls.values())

    age_di_ratio = min(age_selection_rates.values()) / max(age_selection_rates.values())
    age_rec_ratio = min(age_recalls.values()) / max(age_recalls.values())

    audit_report["disparate_impact_analysis"] = {
        "gender_demographic_parity_ratio": float(round(gender_di_ratio, 4)),
        "gender_equal_opportunity_ratio": float(round(gender_rec_ratio, 4)),
        "age_demographic_parity_ratio": float(round(age_di_ratio, 4)),
        "age_equal_opportunity_ratio": float(round(age_rec_ratio, 4)),
        "four_fifths_threshold": 0.80,
    }

    # 4. Verdicts
    passes_gender_parity = gender_rec_ratio >= 0.80
    passes_age_parity = age_rec_ratio >= 0.80

    audit_report["fairness_verdict"] = {
        "gender_parity_passed": bool(passes_gender_parity),
        "age_parity_passed": bool(passes_age_parity),
        "calibration_adequate": all(
            m["brier_score"] < 0.15 for m in list(audit_report["gender_audit"].values()) + list(audit_report["age_group_audit"].values())
        ),
        "overall_fairness_passed": bool(passes_gender_parity and passes_age_parity),
    }

    # Save to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(audit_report, f, indent=2)

    return audit_report


if __name__ == "__main__":
    report = run_fairness_audit()
    print("=" * 60)
    print("MindScope Algorithmic Fairness Audit Summary")
    print("=" * 60)
    print(f"Gender Demographic Parity Ratio: {report['disparate_impact_analysis']['gender_demographic_parity_ratio']:.4f}")
    print(f"Gender Equal Opportunity Ratio:  {report['disparate_impact_analysis']['gender_equal_opportunity_ratio']:.4f}")
    print(f"Age Demographic Parity Ratio:    {report['disparate_impact_analysis']['age_demographic_parity_ratio']:.4f}")
    print(f"Age Equal Opportunity Ratio:     {report['disparate_impact_analysis']['age_equal_opportunity_ratio']:.4f}")
    print(f"Overall Fairness Verdict:        {'PASSED' if report['fairness_verdict']['overall_fairness_passed'] else 'FLAGGED'}")
    print("=" * 60)
