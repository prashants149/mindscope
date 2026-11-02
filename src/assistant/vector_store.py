"""
ChromaDB Vector Store and Document Retrieval Engine for Public Guidance Corpus.
Stores evidence-based mental health resources from WHO, NIMH, Tele-MANAS, and NIMHANS.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

import chromadb
from chromadb.api.models.Collection import Collection

# Ensure OpenMP stability on Windows
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

DEFAULT_CHROMA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "chroma_db"
DEFAULT_CORPUS_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "guidance_corpus" / "corpus_documents.json"
COLLECTION_NAME = "mindscope_guidance"


class GuidanceVectorStore:
    """
    Manages persistent ChromaDB vector index for source-grounded mental health guidance.
    """

    def __init__(self, chroma_dir: Optional[Path] = None):
        self.chroma_dir = chroma_dir or DEFAULT_CHROMA_PATH
        self.chroma_dir.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(self.chroma_dir))
        self.collection: Collection = self.client.get_or_create_collection(name=COLLECTION_NAME)

    def populate_from_corpus(self, corpus_path: Optional[Path] = None, force_reindex: bool = False) -> int:
        """
        Load guidance documents from JSON and index into ChromaDB.
        """
        path = corpus_path or DEFAULT_CORPUS_PATH
        if not path.exists():
            raise FileNotFoundError(f"Corpus document file not found at: {path}")

        with open(path, "r", encoding="utf-8") as f:
            docs = json.load(f)

        existing_count = self.collection.count()
        if existing_count >= len(docs) and not force_reindex:
            return existing_count

        ids = [doc["id"] for doc in docs]
        documents = [doc["content"] for doc in docs]
        metadatas = [
            {
                "title": doc["title"],
                "organization": doc["organization"],
                "url": doc["url"],
            }
            for doc in docs
        ]

        # Upsert documents into collection
        self.collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
        return self.collection.count()

    def search_guidance(self, query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        """
        Perform semantic similarity retrieval over public guidance corpus.
        Returns top-k matching documents with source URLs and organizations.
        """
        if self.collection.count() == 0:
            self.populate_from_corpus()

        results = self.collection.query(
            query_texts=[query],
            n_results=min(top_k, max(1, self.collection.count())),
        )

        retrieved_docs: List[Dict[str, Any]] = []
        if results and "documents" in results and len(results["documents"]) > 0:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if "metadatas" in results else [{}] * len(docs)
            distances = results["distances"][0] if "distances" in results else [0.0] * len(docs)

            for doc_text, meta, dist in zip(docs, metas, distances):
                retrieved_docs.append({
                    "content": doc_text,
                    "title": meta.get("title", "Public Guidance"),
                    "organization": meta.get("organization", "Health Agency"),
                    "url": meta.get("url", "https://telemanas.mohfw.gov.in/"),
                    "relevance_score": round(1.0 - float(dist) if dist is not None else 1.0, 4),
                })

        return retrieved_docs
