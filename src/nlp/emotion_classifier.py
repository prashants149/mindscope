"""
Emotion Classification Engine for Youth Narratives.
Runs on CPU with deterministic crisis interception and calibrated affective distributions.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Union

# Set OpenMP workaround for Windows PyTorch compatibility
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from src.nlp.crisis_safeguard import check_crisis_indicators
from src.utils.constants import MEDICAL_DISCLAIMER, RANDOM_SEED

# Core youth affective taxonomy
EMOTION_CLASSES: List[str] = [
    "anxiety_fear",
    "sadness",
    "anger",
    "stress_overwhelm",
    "joy_optimism",
    "neutral",
]

EMOTION_DISPLAY_MAP: Dict[str, str] = {
    "anxiety_fear": "Anxiety & Fear",
    "sadness": "Sadness & Despair",
    "anger": "Frustration & Anger",
    "stress_overwhelm": "Academic Stress & Overwhelm",
    "joy_optimism": "Joy & Optimism",
    "neutral": "Neutral Reflection",
}


class YouthEmotionClassifier:
    """
    Lightweight CPU emotion classifier for youth reflection texts with
    integrated crisis interception safeguards.
    """

    def __init__(self, model_pipeline: Optional[Pipeline] = None):
        self.model_pipeline = model_pipeline
        self.classes_ = EMOTION_CLASSES

    @classmethod
    def train_baseline_pipeline(cls, df_train: pd.DataFrame) -> "YouthEmotionClassifier":
        """
        Train a calibrated TF-IDF + Logistic Regression emotion classifier on narrative data.
        Fast, lightweight, and deterministic for CPU inference.
        """
        pipeline = Pipeline([
            ("tfidf", TfidfVectorizer(
                ngram_range=(1, 2),
                max_features=2500,
                sublinear_tf=True,
                stop_words="english",
            )),
            ("clf", LogisticRegression(
                C=2.0,
                class_weight="balanced",
                max_iter=1000,
                random_state=RANDOM_SEED,
            )),
        ])
        pipeline.fit(df_train["text"], df_train["emotion"])
        return cls(model_pipeline=pipeline)

    def predict_emotion(self, text: str) -> Dict[str, Any]:
        """
        Analyze narrative text for emotional tone.
        CRITICAL: Intercepts crisis signals (self-harm, suicide) before any inference.
        """
        # 1. Deterministic Crisis Safeguard
        is_crisis, crisis_payload = check_crisis_indicators(text)
        if is_crisis:
            return crisis_payload

        if self.model_pipeline is None:
            raise ValueError("EmotionClassifier model pipeline is not trained or loaded.")

        # 2. Compute probabilities
        probs = self.model_pipeline.predict_proba([text])[0]
        classes = self.model_pipeline.classes_

        prob_dict = {
            cls_name: round(float(prob), 4)
            for cls_name, prob in zip(classes, probs)
        }

        # Identify primary and secondary emotions
        sorted_emotions = sorted(prob_dict.items(), key=lambda x: x[1], reverse=True)
        primary_emotion, primary_conf = sorted_emotions[0]
        secondary_emotion, secondary_conf = sorted_emotions[1]

        # Calculate psychological distress index (sum of negative valence emotions)
        distress_score = prob_dict.get("anxiety_fear", 0.0) + \
                         prob_dict.get("sadness", 0.0) + \
                         prob_dict.get("stress_overwhelm", 0.0)

        if distress_score >= 0.70:
            distress_tier = "High Psychological Distress"
        elif distress_score >= 0.40:
            distress_tier = "Moderate Psychological Distress"
        else:
            distress_tier = "Mild / Low Distress"

        return {
            "is_crisis": False,
            "text": text,
            "primary_emotion": primary_emotion,
            "primary_emotion_label": EMOTION_DISPLAY_MAP.get(primary_emotion, primary_emotion),
            "confidence": round(float(primary_conf), 4),
            "secondary_emotion": secondary_emotion,
            "secondary_emotion_label": EMOTION_DISPLAY_MAP.get(secondary_emotion, secondary_emotion),
            "secondary_confidence": round(float(secondary_conf), 4),
            "emotion_probabilities": prob_dict,
            "distress_index": round(float(distress_score), 4),
            "distress_tier": distress_tier,
            "medical_disclaimer": MEDICAL_DISCLAIMER,
        }

    def save(self, filepath: Union[str, Path]) -> None:
        """Serialize trained pipeline to disk."""
        joblib.dump(self.model_pipeline, filepath)

    @classmethod
    def load(cls, filepath: Union[str, Path]) -> "YouthEmotionClassifier":
        """Load trained pipeline from disk."""
        pipeline = joblib.load(filepath)
        return cls(model_pipeline=pipeline)
