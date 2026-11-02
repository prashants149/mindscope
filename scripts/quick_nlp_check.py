import sys, os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
sys.path.insert(0, r"C:\Users\mrpra\.gemini\antigravity\scratch\mindscope")

print("Importing crisis safeguard...", flush=True)
from src.nlp.crisis_safeguard import check_crisis_indicators
print("OK", flush=True)

# Crisis detection
for t in ["I want to end my life", "Thinking about killing myself", "Started cutting myself"]:
    ok, p = check_crisis_indicators(t)
    assert ok, f"Missed: {t}"
    assert "14416" in p["emergency_helplines"]["tele_manas_short"]
print("Crisis triggers: 3/3 PASSED", flush=True)

for t in ["I killed that exam!", "Dead tired after lab", "I would die for coffee"]:
    ok, _ = check_crisis_indicators(t)
    assert not ok, f"False positive: {t}"
print("Crisis benign: 3/3 PASSED", flush=True)

print("Importing emotion classifier...", flush=True)
import pandas as pd
from src.nlp.emotion_classifier import YouthEmotionClassifier, EMOTION_CLASSES
print("OK", flush=True)

df = pd.read_csv(r"C:\Users\mrpra\.gemini\antigravity\scratch\mindscope\data\nlp\youth_narratives.csv")
clf = YouthEmotionClassifier.train_baseline_pipeline(df)
print("Classifier trained", flush=True)

res = clf.predict_emotion("I have so many submissions due and my hands are trembling.")
assert res["is_crisis"] is False
assert res["primary_emotion"] in EMOTION_CLASSES
assert 0.0 <= res["confidence"] <= 1.0
print("Emotion structure: PASSED", flush=True)

res2 = clf.predict_emotion("I cannot go on anymore, I am going to end my life.")
assert res2["is_crisis"] is True
assert "primary_emotion" not in res2
print("Emotion crisis intercept: PASSED", flush=True)

print("\nAll NLP (non-BERTopic) tests: 5/5 PASSED", flush=True)
