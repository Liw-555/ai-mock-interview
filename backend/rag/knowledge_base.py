"""
Knowledge base loading and chunking.
TODO: P1 - Implement document loading and text chunking.
"""

from typing import List, Dict, Any


def load_knowledge_base(file_path: str) -> List[Dict[str, Any]]:
    """Load knowledge base document and split into chunks."""
    return []


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> List[str]:
    """Split text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    return chunks
