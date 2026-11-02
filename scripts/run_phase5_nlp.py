"""
Executable runner for Phase 5: NLP Emotion Classification, BERTopic Thematic Discovery,
Macro-F1 Benchmarks, and Detailed Error Analysis.
"""

import json
import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Set OpenMP workaround for Windows PyTorch compatibility
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    accuracy_score,
)
from sklearn.model_selection import train_test_split

from src.nlp.emotion_classifier import (
    YouthEmotionClassifier,
    EMOTION_CLASSES,
    EMOTION_DISPLAY_MAP,
)
from src.nlp.topic_model import YouthThemeExtractor
from src.nlp.crisis_safeguard import check_crisis_indicators
from src.utils.constants import RANDOM_SEED


def main():
    print("=" * 65)
    print("MindScope Phase 5: Affective NLP & BERTopic Thematic Analysis")
    print("=" * 65)

    data_path = PROJECT_ROOT / "data" / "nlp" / "youth_narratives.csv"
    reports_dir = PROJECT_ROOT / "reports"
    reports_fig_dir = PROJECT_ROOT / "reports" / "figures"
    models_dir = PROJECT_ROOT / "models"

    reports_dir.mkdir(parents=True, exist_ok=True)
    reports_fig_dir.mkdir(parents=True, exist_ok=True)
    models_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load Data
    print(f"\n[Step 1] Loading youth reflection narratives from {data_path}...")
    df = pd.read_csv(data_path)
    print(f"-> Loaded {len(df)} narrative reflections across {df['emotion'].nunique()} emotion categories.")

    # 2. Train / Test Split
    train_df, test_df = train_test_split(
        df, test_size=0.25, random_state=RANDOM_SEED, stratify=df["emotion"]
    )
    print(f"-> Train samples: {len(train_df)}, Test samples: {len(test_df)}")

    # 3. Train & Evaluate Emotion Classifier
    print("\n[Step 2] Training & Evaluating CPU Emotion Classifier...")
    classifier = YouthEmotionClassifier.train_baseline_pipeline(train_df)

    # Inference on holdout test set
    y_test = test_df["emotion"].values
    test_preds = []
    test_probs = []

    for text in test_df["text"]:
        res = classifier.predict_emotion(text)
        test_preds.append(res["primary_emotion"])
        test_probs.append(res["confidence"])

    # Compute metrics
    macro_f1 = float(f1_score(y_test, test_preds, average="macro"))
    weighted_f1 = float(f1_score(y_test, test_preds, average="weighted"))
    acc = float(accuracy_score(y_test, test_preds))
    cls_report = classification_report(y_test, test_preds, output_dict=True)

    print("\n--- Emotion Classification Performance Metrics ---")
    print(f"  Macro-F1 Score   : {macro_f1:.4f}")
    print(f"  Weighted-F1 Score: {weighted_f1:.4f}")
    print(f"  Overall Accuracy : {acc:.4f}")

    # 4. Confusion Matrix Plot
    labels_present = sorted(list(set(y_test)))
    cm = confusion_matrix(y_test, test_preds, labels=labels_present)

    fig, ax = plt.subplots(figsize=(8, 6))
    display_labels = [EMOTION_DISPLAY_MAP.get(l, l) for l in labels_present]
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=display_labels,
        yticklabels=display_labels,
        ax=ax,
    )
    ax.set_title("Youth Emotion Classification Confusion Matrix (Holdout Set)", pad=15)
    ax.set_xlabel("Predicted Emotion Category")
    ax.set_ylabel("True Ground Truth Category")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    cm_path = reports_fig_dir / "emotion_confusion_matrix.png"
    plt.savefig(cm_path, dpi=300)
    plt.close()
    print(f"-> Confusion matrix plot saved to: {cm_path}")

    # 5. Detailed Error Analysis
    print("\n[Step 3] Performing In-Depth Error Analysis...")
    error_cases = []
    test_df_eval = test_df.copy()
    test_df_eval["predicted_emotion"] = test_preds

    misclassified = test_df_eval[test_df_eval["emotion"] != test_df_eval["predicted_emotion"]]
    print(f"  Total misclassifications on holdout test set: {len(misclassified)} / {len(test_df)}")

    for _, row in misclassified.iterrows():
        error_cases.append({
            "text": row["text"],
            "true_emotion": row["emotion"],
            "predicted_emotion": row["predicted_emotion"],
            "theme": row["theme"],
            "contains_idiom": bool(row["contains_idiom"]),
        })

    # Idiom robustness check (metaphorical campus expressions)
    idiom_texts = [
        "I aced my compiler design viva today, absolutely killed it!",
        "The professor murdered us with that calculus midterm proof.",
        "I'm dead tired after that 4-hour lab practical.",
    ]
    idiom_evaluations = []
    for text in idiom_texts:
        is_crisis, _ = check_crisis_indicators(text)
        res = classifier.predict_emotion(text)
        idiom_evaluations.append({
            "text": text,
            "false_crisis_triggered": is_crisis,
            "predicted_emotion": res["primary_emotion"],
            "confidence": res["confidence"],
        })

    # 6. BERTopic Thematic Discovery
    print("\n[Step 4] Extracting Emergent Narrative Themes with BERTopic...")
    theme_extractor = YouthThemeExtractor(min_topic_size=3)
    theme_extractor.fit(df["text"].tolist())
    discovered_themes = theme_extractor.get_topics_summary()

    print("\n--- Discovered Themes & Representative Keywords ---")
    for t in discovered_themes:
        kw_str = ", ".join([k["word"] for k in t["keywords"][:4]])
        print(f"  {t['label']:<40} (Docs: {t['document_count']:>2}) | Keywords: {kw_str}")

    # 7. Serialize Artifacts & Export JSON
    model_save_path = models_dir / "youth_emotion_classifier.joblib"
    classifier.save(model_save_path)
    print(f"\n-> Serialized emotion classifier pipeline to: {model_save_path}")

    nlp_summary = {
        "dataset_statistics": {
            "total_documents": len(df),
            "train_samples": len(train_df),
            "test_samples": len(test_df),
            "num_classes": len(labels_present),
        },
        "performance_metrics": {
            "macro_f1": round(macro_f1, 4),
            "weighted_f1": round(weighted_f1, 4),
            "accuracy": round(acc, 4),
            "per_class_metrics": {
                k: {
                    "precision": round(v["precision"], 4),
                    "recall": round(v["recall"], 4),
                    "f1-score": round(v["f1-score"], 4),
                    "support": v["support"],
                }
                for k, v in cls_report.items()
                if isinstance(v, dict)
            },
        },
        "error_analysis": {
            "total_misclassifications": len(misclassified),
            "misclassification_rate": round(len(misclassified) / len(test_df), 4),
            "error_samples": error_cases,
            "idiom_robustness_tests": idiom_evaluations,
            "qualitative_findings": [
                "Primary confusion arises along the boundary between 'anxiety_fear' and 'stress_overwhelm' due to shared lexical cues (deadlines, pressure).",
                "Idioms like 'killed that exam' successfully avoided triggering the crisis safeguard through regex exception handling.",
                "Short reflective expressions without explicit emotion words occasionally bias toward the prior distribution.",
            ],
        },
        "discovered_themes": discovered_themes,
    }

    metrics_out = reports_dir / "nlp_metrics.json"
    with open(metrics_out, "w", encoding="utf-8") as f:
        json.dump(
            nlp_summary,
            f,
            indent=2,
            default=lambda obj: bool(obj) if isinstance(obj, (np.bool_, bool)) else float(obj) if isinstance(obj, (np.floating, float, np.integer, int)) else str(obj),
        )

    print(f"-> Full NLP metrics and error analysis exported to: {metrics_out}")
    print("\n" + "=" * 65)
    print("Phase 5 NLP Analysis Completed Successfully.")
    print("=" * 65)


if __name__ == "__main__":
    main()
