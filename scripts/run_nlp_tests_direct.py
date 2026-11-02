"""
Direct NLP test runner — avoids pytest collection hanging on BERTopic import.
Runs crisis safeguard + emotion classifier tests inline, then BERTopic separately.
"""
import os
import sys
import traceback
from pathlib import Path

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

passed = 0
failed = 0
errors = []


def run_test(name, fn):
    global passed, failed
    try:
        fn()
        print(f"  PASSED  {name}")
        passed += 1
    except Exception as e:
        print(f"  FAILED  {name}: {e}")
        failed += 1
        errors.append((name, traceback.format_exc()))


# ── Crisis Safeguard Tests ────────────────────────────────────────────────────
print("\n[1/3] Crisis Safeguard Tests")
from src.nlp.crisis_safeguard import check_crisis_indicators

def t_crisis_triggers():
    crisis_inputs = [
        "I feel like ending my life, I can't take this pressure anymore.",
        "Thinking about killing myself tonight in my hostel room.",
        "I want to die, nobody cares about me anyway.",
        "Started cutting myself because of academic stress.",
    ]
    for text in crisis_inputs:
        is_crisis, payload = check_crisis_indicators(text)
        assert is_crisis is True, f"Missed crisis: {text}"
        assert "14416" in payload["emergency_helplines"]["tele_manas_short"]
        assert "1800-891-4416" in payload["emergency_helplines"]["tele_manas_toll_free"]
        assert "112" in payload["emergency_helplines"]["national_emergency"]
        assert "medical_disclaimer" in payload

def t_crisis_benign():
    benign_inputs = [
        "I totally killed that exam today, feeling great!",
        "The professor murdered us with that calculus midterm proof.",
        "I am dead tired after that 4-hour lab practical.",
        "I would die for a cup of coffee right now.",
    ]
    for text in benign_inputs:
        is_crisis, _ = check_crisis_indicators(text)
        assert is_crisis is False, f"False positive on: {text}"

run_test("test_crisis_safeguard_triggers_on_self_harm", t_crisis_triggers)
run_test("test_crisis_safeguard_ignores_benign_campus_idioms", t_crisis_benign)

# ── Emotion Classifier Tests ──────────────────────────────────────────────────
print("\n[2/3] Emotion Classifier Tests")
import pandas as pd
from src.nlp.emotion_classifier import YouthEmotionClassifier, EMOTION_CLASSES

data_path = PROJECT_ROOT / "data" / "nlp" / "youth_narratives.csv"
df = pd.read_csv(data_path)
clf = YouthEmotionClassifier.train_baseline_pipeline(df)

def t_emotion_structure():
    res = clf.predict_emotion("I have so many project submissions due tomorrow and my hands are trembling.")
    assert res["is_crisis"] is False
    assert res["primary_emotion"] in EMOTION_CLASSES
    assert 0.0 <= res["confidence"] <= 1.0
    probs = res["emotion_probabilities"]
    assert abs(sum(probs.values()) - 1.0) < 0.01
    assert "distress_index" in res
    assert res["distress_tier"] in ["High Psychological Distress", "Moderate Psychological Distress", "Mild / Low Distress"]
    assert "medical_disclaimer" in res

def t_emotion_crisis_intercept():
    res = clf.predict_emotion("I cannot go on anymore, I am going to end my life.")
    assert res["is_crisis"] is True
    assert "tele_manas_short" in res["emergency_helplines"]
    assert "primary_emotion" not in res

run_test("test_emotion_classifier_output_structure", t_emotion_structure)
run_test("test_emotion_classifier_intercepts_crisis", t_emotion_crisis_intercept)

# ── BERTopic Tests ────────────────────────────────────────────────────────────
print("\n[3/3] BERTopic Theme Extractor Test")
from src.nlp.topic_model import YouthThemeExtractor

def t_bertopic():
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

run_test("test_bertopic_theme_extractor", t_bertopic)

# ── Summary ───────────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"NLP Tests: {passed} passed, {failed} failed out of {passed+failed}")
if errors:
    for name, tb in errors:
        print(f"\n--- {name} ---\n{tb}")
print(f"{'='*60}")
sys.exit(0 if failed == 0 else 1)
