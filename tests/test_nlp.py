"""
Unit tests for NLP Emotion Classification, Crisis Safeguards, and BERTopic Extraction.
"""

import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Set OpenMP workaround for Windows PyTorch compatibility
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import pytest
import numpy as np
import pandas as pd

from src.nlp.crisis_safeguard import check_crisis_indicators
from src.nlp.emotion_classifier import YouthEmotionClassifier, EMOTION_CLASSES
from src.nlp.topic_model import YouthThemeExtractor


def test_crisis_safeguard_triggers_on_self_harm():
    """Verify crisis safeguard intercepts explicit and implicit self-harm language."""
    crisis_inputs = [
        "I feel like ending my life, I can't take this pressure anymore.",
        "Thinking about killing myself tonight in my hostel room.",
        "I want to die, nobody cares about me anyway.",
        "Started cutting myself because of academic stress.",
    ]
    for text in crisis_inputs:
        is_crisis, payload = check_crisis_indicators(text)
        assert is_crisis is True, f"Failed to detect crisis in: '{text}'"
        assert payload["is_crisis"] is True
        assert "14416" in payload["emergency_helplines"]["tele_manas_short"]
        assert "1800-891-4416" in payload["emergency_helplines"]["tele_manas_toll_free"]
        assert "112" in payload["emergency_helplines"]["national_emergency"]
        assert "medical_disclaimer" in payload


def test_crisis_safeguard_ignores_benign_campus_idioms():
    """Verify campus slang and idioms do not trigger false positive crisis alarms."""
    benign_inputs = [
        "I totally killed that exam today, feeling great!",
        "The professor murdered us with that calculus midterm proof.",
        "I am dead tired after that 4-hour lab practical.",
        "I would die for a cup of coffee right now.",
    ]
    for text in benign_inputs:
        is_crisis, _ = check_crisis_indicators(text)
        assert is_crisis is False, f"False positive crisis triggered on benign text: '{text}'"


@pytest.fixture(scope="module")
def trained_classifier():
    data_path = PROJECT_ROOT / "data" / "nlp" / "youth_narratives.csv"
    df = pd.read_csv(data_path)
    clf = YouthEmotionClassifier.train_baseline_pipeline(df)
    return clf


def test_emotion_classifier_output_structure(trained_classifier):
    """Verify emotion prediction outputs valid probabilities, distress index, and disclaimer."""
    sample_text = "I have so many project submissions due tomorrow and my hands are trembling."
    res = trained_classifier.predict_emotion(sample_text)

    assert res["is_crisis"] is False
    assert res["primary_emotion"] in EMOTION_CLASSES
    assert 0.0 <= res["confidence"] <= 1.0
    
    # Check probabilities sum to ~1.0
    probs = res["emotion_probabilities"]
    prob_sum = sum(probs.values())
    assert abs(prob_sum - 1.0) < 0.01

    assert "distress_index" in res
    assert res["distress_tier"] in ["High Psychological Distress", "Moderate Psychological Distress", "Mild / Low Distress"]
    assert "medical_disclaimer" in res


def test_emotion_classifier_intercepts_crisis(trained_classifier):
    """Verify classifier halts and returns crisis payload if self-harm text is provided."""
    crisis_text = "I cannot go on anymore, I am going to end my life."
    res = trained_classifier.predict_emotion(crisis_text)
    
    assert res["is_crisis"] is True
    assert "tele_manas_short" in res["emergency_helplines"]
    assert "primary_emotion" not in res  # Inference should be halted


def test_bertopic_theme_extractor():
    """Verify topic extractor identifies themes and keywords on narrative reflections."""
    sample_corpus = [
        "Finals week is approaching and I have three project submissions due Friday.",
        "I couldn't sleep until 4 AM again last night because of exam worry.",
        "I feel like no matter how hard I study, my grades never reflect it.",
        "All my friends got internship offers and I haven't received a call.",
        "Why do professors schedule surprise quizzes right after midterms?",
        "I am juggling two part-time tutoring jobs while managing lab courses.",
        "My group project partners haven't contributed any code.",
        "I just got accepted for a research conference presentation!",
        "Finished the machine learning assignment and went for an evening run.",
        "Attending operating systems lecture and taking notes.",
        "The campus library closes at 8 PM during exam week.",
        "I feel lonely in the hostel with everyone studying alone.",
    ]
    extractor = YouthThemeExtractor(min_topic_size=2)
    extractor.fit(sample_corpus)
    summary = extractor.get_topics_summary()

    assert len(summary) >= 1
    assert "topic_id" in summary[0]
    assert "keywords" in summary[0]
    assert len(summary[0]["keywords"]) > 0
