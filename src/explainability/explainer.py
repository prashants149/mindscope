"""
Explainability engine for MindScope using SHAP (SHapley Additive exPlanations).
Provides global feature attribution rankings, local single-student risk breakdowns,
and plain-English summaries enforcing epistemic guardrails (associations != causation).
"""

from typing import Dict, Any, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
import shap
from sklearn.pipeline import Pipeline
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

from src.models.pipeline import NUMERICAL_FEATURES, CATEGORICAL_FEATURES
from src.utils.constants import MEDICAL_DISCLAIMER

# Human-readable label mappings for clean reporting and UI
FEATURE_LABEL_MAP: Dict[str, str] = {
    "age": "Age",
    "study_year": "Undergraduate Year",
    "sleep_hours": "Sleep Duration (hrs/night)",
    "screen_time_hours": "Screen Time (hrs/day)",
    "academic_pressure": "Academic Pressure (1-5)",
    "social_support": "Social Support Network (1-5)",
    "financial_stress": "Financial Burden (1-5)",
    "physical_activity_hours": "Physical Activity (hrs/week)",
    "gender_Male": "Gender: Male",
    "gender_Non-Binary": "Gender: Non-Binary",
}

EPISTEMIC_GUARDRAIL_NOTICE: str = (
    "CAUSAL WARNING: These SHAP values quantify predictive association and model attribution only. "
    "Statistical associations are NOT causal mechanisms. A high feature attribution does not imply "
    "that modifying this variable will causally reduce depression risk. To estimate true intervention "
    "impacts, refer to MindScope's Structural Causal Inference Engine."
)


class MindScopeExplainer:
    """
    Unified SHAP Explainer supporting both linear and tree models with
    automatic preprocessor feature name resolution.
    """

    def __init__(self, model_pipeline: Union[Pipeline, CalibratedClassifierCV], background_df: pd.DataFrame):
        self.raw_model = model_pipeline
        self.background_df = background_df.copy()
        
        # Extract underlying Pipeline and Classifier
        if isinstance(model_pipeline, CalibratedClassifierCV):
            # CalibratedClassifierCV wraps an estimator (or calibrated_classifiers_)
            if hasattr(model_pipeline, "estimator") and model_pipeline.estimator is not None:
                self.pipeline = model_pipeline.estimator
            else:
                self.pipeline = model_pipeline.calibrated_classifiers_[0].estimator
        elif isinstance(model_pipeline, Pipeline):
            self.pipeline = model_pipeline
        else:
            raise ValueError(f"Unsupported model type: {type(model_pipeline)}")

        self.preprocessor = self.pipeline.named_steps["preprocessor"]
        self.classifier = self.pipeline.named_steps["classifier"]

        # Transform background data to fit explainer
        feature_cols = NUMERICAL_FEATURES + CATEGORICAL_FEATURES
        self.feature_cols = feature_cols
        X_bg = self.background_df[feature_cols]
        self.X_bg_trans = self.preprocessor.transform(X_bg)

        # Retrieve and clean transformed feature names
        raw_names = self.preprocessor.get_feature_names_out()
        self.transformed_names = [
            name.replace("num__", "").replace("cat__", "") for name in raw_names
        ]
        self.display_names = [
            FEATURE_LABEL_MAP.get(name, name) for name in self.transformed_names
        ]

        # Initialize appropriate SHAP Explainer
        if isinstance(self.classifier, (XGBClassifier, RandomForestClassifier)):
            self.explainer = shap.TreeExplainer(self.classifier)
            self.explainer_type = "tree"
        elif isinstance(self.classifier, LogisticRegression):
            self.explainer = shap.LinearExplainer(self.classifier, self.X_bg_trans)
            self.explainer_type = "linear"
        else:
            self.explainer = shap.Explainer(self.classifier.predict_proba, self.X_bg_trans)
            self.explainer_type = "general"

    def get_transformed_df(self, X: pd.DataFrame) -> pd.DataFrame:
        """Transform raw input dataframe to preprocessed feature matrix with readable column names."""
        trans_array = self.preprocessor.transform(X[self.feature_cols])
        return pd.DataFrame(trans_array, columns=self.transformed_names)

    def explain_dataset(self, X: pd.DataFrame) -> shap.Explanation:
        """Compute SHAP Explanation object across a dataset."""
        X_trans = self.get_transformed_df(X)
        shap_vals = self.explainer(X_trans.values)
        
        # Format feature names
        shap_vals.feature_names = self.display_names
        return shap_vals

    def get_global_importance(self, X: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Compute mean absolute SHAP feature importance across the dataset.
        """
        explanation = self.explain_dataset(X)
        vals = explanation.values
        # If binary classification with 2 output dimensions in tree explainer, take positive class
        if len(vals.shape) == 3 and vals.shape[2] == 2:
            vals = vals[:, :, 1]

        mean_abs = np.mean(np.abs(vals), axis=0)
        sorted_indices = np.argsort(mean_abs)[::-1]

        ranking: List[Dict[str, Any]] = []
        for idx in sorted_indices:
            ranking.append({
                "feature": self.transformed_names[idx],
                "display_name": self.display_names[idx],
                "mean_abs_shap": round(float(mean_abs[idx]), 4),
            })
        return ranking

    def explain_single_student(self, student_input: Union[Dict[str, Any], pd.Series, pd.DataFrame]) -> Dict[str, Any]:
        """
        Generate local SHAP explanation, plain-English breakdown, and epistemic guardrails
        for a single student's profile.
        """
        if isinstance(student_input, dict):
            df_single = pd.DataFrame([student_input])
        elif isinstance(student_input, pd.Series):
            df_single = pd.DataFrame([student_input.to_dict()])
        else:
            df_single = student_input.copy()

        # Predict calibrated risk probability
        prob_dist = self.raw_model.predict_proba(df_single[self.feature_cols])[0]
        prob_risk = float(prob_dist[1])

        # Compute SHAP values for single instance
        X_trans = self.get_transformed_df(df_single)
        single_explanation = self.explainer(X_trans.values)[0]
        
        shap_values = single_explanation.values
        if len(shap_values.shape) == 2 and shap_values.shape[1] == 2:
            shap_values = shap_values[:, 1]
            base_value = float(single_explanation.base_values[1])
        else:
            base_value = float(single_explanation.base_values)

        # Combine features with values and attributions
        contributions: List[Dict[str, Any]] = []
        for i, (name, disp_name) in enumerate(zip(self.transformed_names, self.display_names)):
            raw_feature_val = X_trans.iloc[0, i]
            shap_val = float(shap_values[i])
            contributions.append({
                "feature": name,
                "display_name": disp_name,
                "feature_value": round(float(raw_feature_val), 2),
                "shap_value": round(shap_val, 4),
                "direction": "Risk Escalator" if shap_val > 0 else "Protective Factor",
            })

        # Sort factors by impact magnitude
        risk_escalators = sorted(
            [c for c in contributions if c["shap_value"] > 0],
            key=lambda x: x["shap_value"],
            reverse=True,
        )
        protective_factors = sorted(
            [c for c in contributions if c["shap_value"] < 0],
            key=lambda x: abs(x["shap_value"]),
            reverse=True,
        )

        # Risk level determination
        if prob_risk >= 0.65:
            risk_tier = "Elevated Risk Indicator"
        elif prob_risk >= 0.35:
            risk_tier = "Moderate Risk Indicator"
        else:
            risk_tier = "Low Risk Indicator"

        # Construct Plain-English Explanation
        top_risks_text = (
            ", ".join([f"{r['display_name']} (+{r['shap_value']:.2f})" for r in risk_escalators[:3]])
            if risk_escalators else "No significant risk escalators identified"
        )
        top_prot_text = (
            ", ".join([f"{p['display_name']} ({p['shap_value']:.2f})" for p in protective_factors[:3]])
            if protective_factors else "No significant protective factors identified"
        )

        plain_english_summary = (
            f"The model estimates a {prob_risk * 100:.1f}% risk score ({risk_tier}). "
            f"The primary factors statistically associated with increased risk for this profile are: {top_risks_text}. "
            f"The primary factors buffering or reducing predicted risk are: {top_prot_text}."
        )

        return {
            "predicted_risk_probability": round(prob_risk, 4),
            "risk_tier": risk_tier,
            "base_value": round(base_value, 4),
            "top_risk_escalators": risk_escalators[:3],
            "top_protective_factors": protective_factors[:3],
            "all_feature_contributions": sorted(contributions, key=lambda x: abs(x["shap_value"]), reverse=True),
            "plain_english_summary": plain_english_summary,
            "epistemic_guardrail": EPISTEMIC_GUARDRAIL_NOTICE,
            "medical_disclaimer": MEDICAL_DISCLAIMER,
        }
