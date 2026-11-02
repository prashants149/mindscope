"""MindScope NLP and Safe Text Analytics Package."""
from .crisis_safeguard import check_crisis_indicators
from .emotion_classifier import YouthEmotionClassifier, EMOTION_CLASSES, EMOTION_DISPLAY_MAP


def __getattr__(name):
    """Lazy-load heavy dependencies (BERTopic/sentence-transformers) on first access."""
    if name == "YouthThemeExtractor":
        from .topic_model import YouthThemeExtractor
        return YouthThemeExtractor
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "check_crisis_indicators",
    "YouthEmotionClassifier",
    "EMOTION_CLASSES",
    "EMOTION_DISPLAY_MAP",
    "YouthThemeExtractor",
]
