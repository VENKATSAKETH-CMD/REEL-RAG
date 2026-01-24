"""
Phase 2 — Embedding Service

Handles text-to-vector conversion for semantic search and similarity.
Supports multiple backends (stub, OpenAI, etc.)
"""

import os
from typing import List

EMBED_DIM = int(os.getenv("EMBED_DIM", "1536"))


def embed_text(text: str) -> List[float]:
    """
    Convert text to embedding vector.

    Args:
        text: Text to embed

    Returns:
        List of floats representing the embedding vector

    Raises:
        NotImplementedError: If backend is not yet implemented
        ValueError: If EMBED_MODE is invalid
    """
    embed_mode = os.getenv("EMBED_MODE", "stub").lower()

    if embed_mode == "stub":
        # Return deterministic fake vector based on text length
        n = EMBED_DIM
        base = (len(text) % 100) / 100.0
        return [base for _ in range(n)]

    elif embed_mode == "openai":
        raise NotImplementedError("OpenAI embeddings not wired yet")

    else:
        raise ValueError(f"Invalid EMBED_MODE: {embed_mode}. Must be 'stub' or 'openai'")
