"""
Model definitions, feature preprocessors, and calibration wrappers for MindScope.
"""

from typing import List, Tuple, Dict, Any
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV
from xgboost import XGBClassifier

from src.utils.constants import RANDOM_SEED

NUMERICAL_FEATURES: List[str] = [
    "age",
    "study_year",
    "sleep_hours",
    "screen_time_hours",
    "academic_pressure",
    "social_support",
    "financial_stress",
    "physical_activity_hours",
]

CATEGORICAL_FEATURES: List[str] = [
    "gender",
]

TARGET_COLUMN: str = "depression"


def build_preprocessor() -> ColumnTransformer:
    """Construct ColumnTransformer for numerical scaling and categorical encoding."""
    num_pipeline = Pipeline([
        ("scaler", StandardScaler()),
    ])
    cat_pipeline = Pipeline([
        ("onehot", OneHotEncoder(handle_unknown="ignore", drop="first", sparse_output=False)),
    ])
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", num_pipeline, NUMERICAL_FEATURES),
            ("cat", cat_pipeline, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )
    return preprocessor


def get_model_specs(scale_pos_weight: float = 1.0) -> Dict[str, Pipeline]:
    """
    Construct uncalibrated candidate model pipelines with class-imbalance weighting.
    """
    preprocessor = build_preprocessor()

    models = {
        "Logistic_Regression": Pipeline([
            ("preprocessor", preprocessor),
            ("classifier", LogisticRegression(
                class_weight="balanced",
                C=1.0,
                max_iter=1000,
                random_state=RANDOM_SEED,
            )),
        ]),
        "Random_Forest": Pipeline([
            ("preprocessor", preprocessor),
            ("classifier", RandomForestClassifier(
                n_estimators=100,
                max_depth=6,
                class_weight="balanced",
                random_state=RANDOM_SEED,
            )),
        ]),
        "XGBoost": Pipeline([
            ("preprocessor", preprocessor),
            ("classifier", XGBClassifier(
                n_estimators=100,
                max_depth=4,
                learning_rate=0.05,
                scale_pos_weight=scale_pos_weight,
                eval_metric="logloss",
                random_state=RANDOM_SEED,
            )),
        ]),
    }
    return models


def wrap_with_calibration(model_pipeline: Pipeline, cv: int = 3, method: str = "sigmoid") -> CalibratedClassifierCV:
    """
    Wrap estimator pipeline with probability calibration (Platt scaling or isotonic regression).
    """
    return CalibratedClassifierCV(
        estimator=model_pipeline,
        method=method,
        cv=cv,
    )
