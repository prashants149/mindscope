"""
Visualization module for SHAP explanations (Global Beeswarm, Bar Plots,
Dependence Plots, and Local Waterfall Explanations).
"""

from pathlib import Path
from typing import List, Dict, Any
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap

from src.explainability.explainer import MindScopeExplainer


def generate_shap_visualizations(
    explainer: MindScopeExplainer,
    df_eval: pd.DataFrame,
    output_dir: Path,
) -> List[str]:
    """
    Generate and save all publication-ready SHAP explanation figures.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    generated_figures: List[str] = []

    # Compute SHAP explanation for evaluation set
    explanation = explainer.explain_dataset(df_eval)
    X_trans = explainer.get_transformed_df(df_eval)

    # 1. Global Beeswarm Summary Plot
    plt.figure(figsize=(10, 6))
    shap.summary_plot(
        explanation.values,
        features=X_trans.values,
        feature_names=explainer.display_names,
        plot_type="dot",
        show=False,
    )
    plt.title("SHAP Global Feature Attribution Summary (Beeswarm)", pad=15, fontsize=13)
    plt.tight_layout()
    beeswarm_path = output_dir / "shap_summary_beeswarm.png"
    plt.savefig(beeswarm_path, dpi=300)
    plt.close()
    generated_figures.append(str(beeswarm_path))

    # 2. Mean Absolute SHAP Importance Bar Plot
    global_ranking = explainer.get_global_importance(df_eval)
    features = [item["display_name"] for item in global_ranking][::-1]
    importances = [item["mean_abs_shap"] for item in global_ranking][::-1]

    plt.figure(figsize=(9, 6))
    y_pos = np.arange(len(features))
    plt.barh(y_pos, importances, color="#2b5c8f", align="center", alpha=0.85)
    plt.yticks(y_pos, features)
    plt.xlabel("Mean Absolute SHAP Value (|log-odds impact|)")
    plt.title("SHAP Global Feature Importance Ranking", fontsize=13, pad=15)
    plt.tight_layout()
    bar_path = output_dir / "shap_feature_importance_bar.png"
    plt.savefig(bar_path, dpi=300)
    plt.close()
    generated_figures.append(str(bar_path))

    # 3. Dependence Plot: Academic Pressure
    plt.figure(figsize=(8, 5))
    acad_idx = explainer.transformed_names.index("academic_pressure")
    sleep_idx = explainer.transformed_names.index("sleep_hours")
    
    shap.dependence_plot(
        acad_idx,
        explanation.values,
        X_trans.values,
        feature_names=explainer.display_names,
        interaction_index=sleep_idx,
        show=False,
    )
    plt.title("SHAP Dependence: Academic Pressure vs. Sleep Duration", fontsize=12, pad=12)
    plt.tight_layout()
    dep_acad_path = output_dir / "shap_dependence_academic_pressure.png"
    plt.savefig(dep_acad_path, dpi=300)
    plt.close()
    generated_figures.append(str(dep_acad_path))

    # 4. Dependence Plot: Sleep Hours
    plt.figure(figsize=(8, 5))
    screen_idx = explainer.transformed_names.index("screen_time_hours")
    shap.dependence_plot(
        sleep_idx,
        explanation.values,
        X_trans.values,
        feature_names=explainer.display_names,
        interaction_index=screen_idx,
        show=False,
    )
    plt.title("SHAP Dependence: Sleep Duration vs. Screen Time", fontsize=12, pad=12)
    plt.tight_layout()
    dep_sleep_path = output_dir / "shap_dependence_sleep_hours.png"
    plt.savefig(dep_sleep_path, dpi=300)
    plt.close()
    generated_figures.append(str(dep_sleep_path))

    # 5. Local Waterfall Plot: High-Risk Profile
    # Identify sample with highest predicted probability
    probs = explainer.raw_model.predict_proba(df_eval[explainer.feature_cols])[:, 1]
    high_idx = int(np.argmax(probs))
    low_idx = int(np.argmin(probs))

    # High-Risk Waterfall
    fig = plt.figure(figsize=(10, 6))
    shap.plots.waterfall(explanation[high_idx], max_display=10, show=False)
    plt.title(f"SHAP Local Waterfall: High-Risk Profile (P = {probs[high_idx]:.3f})", pad=15, fontsize=12)
    plt.tight_layout()
    wf_high_path = output_dir / "shap_local_waterfall_high_risk.png"
    plt.savefig(wf_high_path, dpi=300)
    plt.close()
    generated_figures.append(str(wf_high_path))

    # 6. Local Waterfall Plot: Low-Risk Profile
    fig = plt.figure(figsize=(10, 6))
    shap.plots.waterfall(explanation[low_idx], max_display=10, show=False)
    plt.title(f"SHAP Local Waterfall: Low-Risk Profile (P = {probs[low_idx]:.3f})", pad=15, fontsize=12)
    plt.tight_layout()
    wf_low_path = output_dir / "shap_local_waterfall_low_risk.png"
    plt.savefig(wf_low_path, dpi=300)
    plt.close()
    generated_figures.append(str(wf_low_path))

    return generated_figures
