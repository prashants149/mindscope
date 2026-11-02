"""
Thematic Analysis and Topic Modeling Engine for Youth Mental Health Narratives using BERTopic.
Discovers latent stress themes, representative keywords, and document-topic distributions.
"""

import os
from typing import Dict, Any, List, Tuple, Optional, Union
from pathlib import Path

# Set OpenMP workaround for Windows PyTorch compatibility
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import pandas as pd
from bertopic import BERTopic
from umap import UMAP
from hdbscan import HDBSCAN
from sklearn.feature_extraction.text import CountVectorizer

from src.utils.constants import RANDOM_SEED


class YouthThemeExtractor:
    """
    BERTopic wrapper tuned for youth mental health reflections.
    Extracts emergent themes like Academic Deadlines, Career Anxiety,
    Sleep Deprivation, and Social Isolation.
    """

    def __init__(self, min_topic_size: int = 3, top_n_words: int = 8):
        self.min_topic_size = min_topic_size
        self.top_n_words = top_n_words
        self.topic_model: Optional[BERTopic] = None

    def fit(self, texts: List[str]) -> "YouthThemeExtractor":
        """
        Fit BERTopic on collection of student narratives.
        """
        # Configure deterministic UMAP for dimensionality reduction
        n_samples = len(texts)
        n_neighbors = min(10, max(2, n_samples // 10))
        umap_model = UMAP(
            n_neighbors=n_neighbors,
            n_components=5,
            min_dist=0.0,
            metric="cosine",
            random_state=RANDOM_SEED,
        )

        # Configure HDBSCAN for density clustering
        hdbscan_model = HDBSCAN(
            min_cluster_size=self.min_topic_size,
            metric="euclidean",
            cluster_selection_method="eom",
            prediction_data=True,
        )

        # Fine-tune topic representations with n-gram vectorizer
        vectorizer_model = CountVectorizer(
            ngram_range=(1, 2),
            stop_words="english",
            min_df=2,
        )

        self.topic_model = BERTopic(
            umap_model=umap_model,
            hdbscan_model=hdbscan_model,
            vectorizer_model=vectorizer_model,
            top_n_words=self.top_n_words,
            calculate_probabilities=True,
            verbose=False,
        )

        self.topic_model.fit(texts)
        return self

    def get_topics_summary(self) -> List[Dict[str, Any]]:
        """
        Extract clean, structured summary of discovered topics and keywords.
        """
        if self.topic_model is None:
            raise ValueError("BERTopic model has not been fitted.")

        info_df = self.topic_model.get_topic_info()
        topics_summary = []

        for _, row in info_df.iterrows():
            topic_id = int(row["Topic"])
            count = int(row["Count"])
            name = str(row["Name"])

            # Retrieve top words and scores
            words_scores = self.topic_model.get_topic(topic_id)
            if words_scores:
                keywords = [{"word": str(w), "c_tf_idf": round(float(s), 4)} for w, s in words_scores[:6]]
                top_words = [w for w, _ in words_scores[:4]]
            else:
                keywords = []
                top_words = []

            # Assign intuitive human-readable topic label
            if topic_id == -1:
                label = "Miscellaneous / Outlier Reflections"
            else:
                label = f"Theme {topic_id}: " + " & ".join([w.title() for w in top_words[:3]])

            topics_summary.append({
                "topic_id": topic_id,
                "label": label,
                "document_count": count,
                "keywords": keywords,
            })

        return topics_summary

    def predict_text_theme(self, text: str) -> Dict[str, Any]:
        """
        Infer topic assignment for an individual student reflection text.
        """
        if self.topic_model is None:
            raise ValueError("BERTopic model has not been fitted.")

        topics, probs = self.topic_model.transform([text])
        topic_id = int(topics[0])
        prob = float(probs[0].max()) if probs is not None and len(probs) > 0 else 0.0

        words_scores = self.topic_model.get_topic(topic_id)
        keywords = [w for w, _ in words_scores[:5]] if words_scores else []

        return {
            "assigned_topic_id": topic_id,
            "confidence": round(prob, 4),
            "theme_keywords": keywords,
        }
