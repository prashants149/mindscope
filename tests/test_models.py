"""
Unit tests for predictive models, preprocessing, calibration, and serialization.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
import numpy as np
import pandas as pd
import joblib

from src.models.pipeline import (
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
    TARGET_COLUMN,
    build_preprocessor,
    get_model_specs,
    wrap_with_calibration,
)
from src.data.generator import generate_synthetic_dataset


@pytest.fixture
def sample_dataset():
    df, _ = generate_synthetic_dataset(n_samples=300, random_seed=42)
    return df


def test_preprocessor_transformation(sample_dataset):
    """Verify preprocessor handles numerical and categorical columns correctly."""
    feature_cols = NUMERICAL_FEATURES + CATEGORICAL_FEATURES
    X = sample_dataset[feature_cols]
    
    preprocessor = build_preprocessor()
    X_transformed = preprocessor.fit_transform(X)
    
    # 8 numerical + 2 one-hot for gender (since Female, Male, Non-Binary with drop='first') = 10 cols
    assert X_transformed.shape[0] == 300
    assert X_transformed.shape[1] >= 10
    assert not np.isnan(X_transformed).any()


def test_all_models_produce_valid_probabilities(sample_dataset):
    """Verify Logistic Regression, Random Forest, and XGBoost predict valid probabilities."""
    feature_cols = NUMERICAL_FEATURES + CATEGORICAL_FEATURES
    X = sample_dataset[feature_cols]
    y = sample_dataset[TARGET_COLUMN].values
    
    models = get_model_specs()
    for name, pipeline in models.items():
        pipeline.fit(X, y)
        probs = pipeline.predict_proba(X)
        
        assert probs.shape == (300, 2), f"{name} probability shape mismatch"
        assert (probs >= 0.0).all() and (probs <= 1.0).all(), f"{name} output probabilities out of [0, 1]"
        np.testing.assert_allclose(probs.sum(axis=1), 1.0, atol=1e-5)


def test_calibrated_model_behavior(sample_dataset):
    """Verify calibration wrapper functions and produces valid risk scores."""
    feature_cols = NUMERICAL_FEATURES + CATEGORICAL_FEATURES
    X = sample_dataset[feature_cols]
    y = sample_dataset[TARGET_COLUMN].values
    
    models = get_model_specs()
    rf_pipe = models["Random_Forest"]
    
    calibrated_rf = wrap_with_calibration(rf_pipe, cv=3, method="sigmoid")
    calibrated_rf.fit(X, y)
    probs = calibrated_rf.predict_proba(X)[:, 1]
    
    assert len(probs) == 300
    assert probs.min() >= 0.0
    assert probs.max() <= 1.0


def test_model_serialization(tmp_path, sample_dataset):
    """Verify joblib dump and reload produces identical probability outputs."""
    feature_cols = NUMERICAL_FEATURES + CATEGORICAL_FEATURES
    X = sample_dataset[feature_cols]
    y = sample_dataset[TARGET_COLUMN].values
    
    models = get_model_specs()
    xgb_pipe = models["XGBoost"]
    calibrated_xgb = wrap_with_calibration(xgb_pipe, cv=2, method="sigmoid")
    calibrated_xgb.fit(X, y)
    
    original_preds = calibrated_xgb.predict_proba(X[:10])[:, 1]
    
    model_file = tmp_path / "test_model.joblib"
    joblib.dump(calibrated_xgb, model_file)
    
    loaded_model = joblib.load(model_file)
    loaded_preds = loaded_model.predict_proba(X[:10])[:, 1]
    
    np.testing.assert_allclose(original_preds, loaded_preds, atol=1e-6)
