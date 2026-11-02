"""
Exploratory Data Analysis (EDA) module for MindScope.
Generates publication-quality figures, correlation matrices, and distribution metrics.
"""

import json
from pathlib import Path
from typing import Dict, Any
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Set aesthetic style
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "figure.titlesize": 15,
})


def generate_eda_reports(df: pd.DataFrame, output_dir: Path) -> Dict[str, Any]:
    """
    Generate all Phase 2 EDA figures and quantitative summary statistics.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    stats: Dict[str, Any] = {}

    # 1. Distribution Overview Figure
    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    
    # Sleep hours
    sns.histplot(df["sleep_hours"], kde=True, ax=axes[0, 0], color="#2b5c8f", bins=20)
    axes[0, 0].set_title("Sleep Duration (Hours/Night)")
    axes[0, 0].set_xlabel("Hours")
    axes[0, 0].axvline(df["sleep_hours"].mean(), color="red", linestyle="--", label=f"Mean: {df['sleep_hours'].mean():.2f}")
    axes[0, 0].legend()

    # Screen time
    sns.histplot(df["screen_time_hours"], kde=True, ax=axes[0, 1], color="#d95f02", bins=20)
    axes[0, 1].set_title("Daily Screen Time (Hours/Day)")
    axes[0, 1].set_xlabel("Hours")
    axes[0, 1].axvline(df["screen_time_hours"].mean(), color="black", linestyle="--", label=f"Mean: {df['screen_time_hours'].mean():.2f}")
    axes[0, 1].legend()

    # Academic pressure
    sns.countplot(x="academic_pressure", hue="academic_pressure", data=df, ax=axes[0, 2], palette="Blues", legend=False)
    axes[0, 2].set_title("Academic Pressure (Likert 1-5)")
    axes[0, 2].set_xlabel("Severity Level")

    # Depression Score
    sns.histplot(df["depression_score"], kde=True, ax=axes[1, 0], color="#7570b3", bins=25)
    axes[1, 0].set_title("Depression Severity (PHQ-9 0-27)")
    axes[1, 0].set_xlabel("PHQ-9 Score")
    axes[1, 0].axvline(10.0, color="crimson", linestyle="-", linewidth=2, label="Moderate Cutoff (>=10)")
    axes[1, 0].legend()

    # Attendance Rate
    sns.histplot(df["attendance_rate"], kde=True, ax=axes[1, 1], color="#1b9e77", bins=20)
    axes[1, 1].set_title("Semester Attendance Rate (%)")
    axes[1, 1].set_xlabel("Attendance %")

    # CGPA
    sns.histplot(df["cgpa"], kde=True, ax=axes[1, 2], color="#e7298a", bins=20)
    axes[1, 2].set_title("Cumulative GPA (10.0 Scale)")
    axes[1, 2].set_xlabel("CGPA")

    plt.tight_layout()
    fig_dist_path = output_dir / "eda_distribution_overview.png"
    plt.savefig(fig_dist_path, dpi=300)
    plt.close(fig)

    # 2. Correlation Matrix Heatmap
    corr_cols = [
        "sleep_hours",
        "screen_time_hours",
        "academic_pressure",
        "social_support",
        "financial_stress",
        "anxiety_score",
        "depression_score",
        "attendance_rate",
        "cgpa",
    ]
    corr_matrix = df[corr_cols].corr()

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        vmin=-0.8,
        vmax=0.8,
        center=0,
        square=True,
        linewidths=0.5,
        cbar_kws={"shrink": 0.8},
        ax=ax,
    )
    ax.set_title("Pairwise Pearson Correlation Matrix (Predictors & Academic Outcomes)", pad=15)
    plt.tight_layout()
    fig_corr_path = output_dir / "eda_correlation_matrix.png"
    plt.savefig(fig_corr_path, dpi=300)
    plt.close(fig)

    # 3. Bivariate Predictors by Depression Status
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    df_plot = df.copy()
    df_plot["Depression Group"] = df_plot["depression"].map({0: "Non-Depressed (<10)", 1: "Depressed (>=10)"})
    palette = {"Non-Depressed (<10)": "#2b5c8f", "Depressed (>=10)": "#d95f02"}

    sns.boxplot(x="Depression Group", y="sleep_hours", hue="Depression Group", data=df_plot, ax=axes[0], palette=palette, legend=False)
    axes[0].set_title("Sleep Duration by Depression Status")
    axes[0].set_ylabel("Hours / Night")

    sns.boxplot(x="Depression Group", y="screen_time_hours", hue="Depression Group", data=df_plot, ax=axes[1], palette=palette, legend=False)
    axes[1].set_title("Screen Time by Depression Status")
    axes[1].set_ylabel("Hours / Day")

    sns.boxplot(x="Depression Group", y="academic_pressure", hue="Depression Group", data=df_plot, ax=axes[2], palette=palette, legend=False)
    axes[2].set_title("Academic Pressure by Depression Status")
    axes[2].set_ylabel("Likert (1-5)")

    plt.tight_layout()
    fig_bivar_path = output_dir / "eda_bivariate_relationships.png"
    plt.savefig(fig_bivar_path, dpi=300)
    plt.close(fig)

    # 4. Downstream Academic Impact (Attendance & CGPA vs Depression)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    sns.regplot(
        x="depression_score",
        y="attendance_rate",
        data=df,
        ax=axes[0],
        scatter_kws={"alpha": 0.25, "color": "#1b9e77"},
        line_kws={"color": "darkred", "linewidth": 2},
    )
    axes[0].set_title("Depression Severity vs. Attendance Rate")
    axes[0].set_xlabel("PHQ-9 Score")
    axes[0].set_ylabel("Attendance Rate (%)")

    sns.regplot(
        x="depression_score",
        y="cgpa",
        data=df,
        ax=axes[1],
        scatter_kws={"alpha": 0.25, "color": "#7570b3"},
        line_kws={"color": "darkblue", "linewidth": 2},
    )
    axes[1].set_title("Depression Severity vs. CGPA")
    axes[1].set_xlabel("PHQ-9 Score")
    axes[1].set_ylabel("Cumulative GPA (10.0)")

    plt.tight_layout()
    fig_downstream_path = output_dir / "eda_downstream_impacts.png"
    plt.savefig(fig_downstream_path, dpi=300)
    plt.close(fig)

    # Summary Statistics Compilation
    dep_0 = df[df["depression"] == 0]
    dep_1 = df[df["depression"] == 1]

    stats = {
        "dataset_rows": int(len(df)),
        "depression_prevalence": float(df["depression"].mean()),
        "correlations_with_depression": {
            col: round(float(corr_matrix.loc[col, "depression_score"]), 3)
            for col in corr_cols
        },
        "sleep_hours": {
            "overall_mean": round(float(df["sleep_hours"].mean()), 2),
            "non_depressed_mean": round(float(dep_0["sleep_hours"].mean()), 2),
            "depressed_mean": round(float(dep_1["sleep_hours"].mean()), 2),
        },
        "screen_time_hours": {
            "overall_mean": round(float(df["screen_time_hours"].mean()), 2),
            "non_depressed_mean": round(float(dep_0["screen_time_hours"].mean()), 2),
            "depressed_mean": round(float(dep_1["screen_time_hours"].mean()), 2),
        },
        "academic_pressure": {
            "overall_mean": round(float(df["academic_pressure"].mean()), 2),
            "non_depressed_mean": round(float(dep_0["academic_pressure"].mean()), 2),
            "depressed_mean": round(float(dep_1["academic_pressure"].mean()), 2),
        },
        "downstream_impacts": {
            "mean_attendance_non_depressed": round(float(dep_0["attendance_rate"].mean()), 2),
            "mean_attendance_depressed": round(float(dep_1["attendance_rate"].mean()), 2),
            "mean_cgpa_non_depressed": round(float(dep_0["cgpa"].mean()), 2),
            "mean_cgpa_depressed": round(float(dep_1["cgpa"].mean()), 2),
        },
        "figures_created": [
            str(fig_dist_path),
            str(fig_corr_path),
            str(fig_bivar_path),
            str(fig_downstream_path),
        ],
    }

    return stats
