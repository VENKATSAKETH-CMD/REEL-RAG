# Phase 2 – Chunking helper for Copilot
#
# Implement a simple text chunker for transcripts.
#
# Requirements:
# - Expose:
#       from typing import List, Dict
#       def chunk_text(full_text: str, max_chars: int = 2000, overlap: int = 300) -> List[Dict]:
#           """
#           Return a list of chunks, each dict containing:
#               {"index": <int>, "text": <str>}
#           """
#
# - Behavior:
#   - Slice the string into segments of at most max_chars characters.
#   - Use sliding-window with overlap characters between consecutive chunks.
#   - Example:
#       start = 0
#       end = min(start + max_chars, len(full_text))
#       chunk = full_text[start:end]
#       then next start = max(0, end - overlap)
#   - Stop when we've consumed the entire string.
#
# - If full_text is empty or only whitespace, return an empty list.
#
# - Keep it simple; sentence-aware logic is NOT required for MVP.

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, TYPE_CHECKING, List, Dict
import os
from sqlalchemy import Column

from pgvector.sqlalchemy import Vector

EMBED_DIM = int(os.getenv("EMBED_DIM", "1536"))

if TYPE_CHECKING:
    from app.models.reel import Reel


def chunk_text(
    full_text: str, max_chars: int = 2000, overlap: int = 300
) -> List[Dict[str, any]]:
    """
    Split text into overlapping chunks using a sliding window approach.

    Args:
        full_text: The text to chunk
        max_chars: Maximum characters per chunk (default: 2000)
        overlap: Number of characters to overlap between chunks (default: 300)

    Returns:
        List of dicts with {"index": int, "text": str}
        Returns empty list if text is empty or only whitespace
    """
    # Return empty list for empty or whitespace-only text
    if not full_text or not full_text.strip():
        return []

    chunks = []
    start = 0
    index = 0

    while start < len(full_text):
        # Calculate end position
        end = min(start + max_chars, len(full_text))

        # Extract chunk
        chunk = full_text[start:end]

        # Add to results
        chunks.append({"index": index, "text": chunk})

        # Move to next chunk start position
        start = max(0, end - overlap)

        # Prevent infinite loop if we're at the end
        if end == len(full_text):
            break

        index += 1

    return chunks


class ReelChunk(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    reel_id: int = Field(foreign_key="reel.id")
    chunk_index: int
    text: str
    # embedding is a native pgvector column (used for similarity search)
    embedding: Optional[List[float]] = Field(default=None, sa_column=Column(Vector(EMBED_DIM)))
    model_name: str
    created_at: datetime = Field(default_factory=datetime.now)

    # Relationship back to Reel
    reel: Optional["Reel"] = Relationship(back_populates="chunks")

    # Accessor: embedding is stored as vector column and can be accessed as Python list
    def get_embedding(self):
        return self.embedding


