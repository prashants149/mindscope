"""MindScope Safe Assistant Package.

Vector store (sentence-transformers / ChromaDB) is loaded lazily
to avoid hangs during pytest collection on Python 3.13.
"""


def __getattr__(name):
    """Lazy-load heavy assistant dependencies on first access."""
    if name == "GuidanceVectorStore":
        from .vector_store import GuidanceVectorStore
        return GuidanceVectorStore
    if name == "SafeSupportAssistant":
        from .safe_agent import SafeSupportAssistant
        return SafeSupportAssistant
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["GuidanceVectorStore", "SafeSupportAssistant"]
