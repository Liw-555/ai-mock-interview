"""
Embedding model wrapper.
TODO: P1 - Integrate user's free embedding model.
"""

from typing import List


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Embed a list of texts into vectors."""
    # Placeholder: return zero vectors
    return [[0.0] * 768 for _ in texts]


def embed_query(text: str) -> List[float]:
    """Embed a single query text."""
    # Placeholder: return zero vector
    return [0.0] * 768
