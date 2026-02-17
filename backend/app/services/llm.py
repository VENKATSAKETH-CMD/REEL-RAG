"""
Phase 3 — LLM Service (DEPRECATED - For Reference Only)

IMPORTANT: This module is NOT USED in the current codebase.
Chat answers are generated in app.services.rag.answer_reel_question() using OpenAI directly.

Kept here for:
1. Reference/documentation of early design attempts
2. Easy rollback if stub-mode LLM becomes necessary

For actual chat generation, see: app.services.rag.answer_reel_question()
"""

import os
from typing import List, Dict


def answer_question_from_chunks(
    question: str,
    chunks: List[Dict],
) -> str:
    """
    DEPRECATED - Not currently used.
    
    This function was an earlier approach to answer generation using stub mode.
    The current system uses OpenAI chat directly in answer_reel_question().
    """
    llm_mode = os.getenv("LLM_MODE", "stub").lower()

    if llm_mode == "stub":
        # Stub mode: deterministic, no network calls
        if not chunks:
            return "I don't have any transcript context yet for this reel."

        # Build a simple answer from chunks
        context = "\n".join([chunk["text"] for chunk in chunks])
        return (
            f"Based on the transcript, here is a rough answer:\n\n"
            f"Question: {question}\n\n"
            f"Context from transcript:\n{context}\n\n"
            f"[This is a stub answer generated from transcript chunks. "
            f"A real LLM would provide a more comprehensive response.]"
        )

    else:
        raise ValueError(f"Invalid LLM_MODE: {llm_mode}. LLM service is deprecated. Use rag.answer_reel_question() instead.")
