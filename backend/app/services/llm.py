"""
Phase 3 — LLM (Language Model) Service

Handles answer generation from retrieved chunks using different backends.
Supports stub mode (free, deterministic) and OpenAI mode (to be implemented).
"""

import os
from typing import List, Dict
import openai


def answer_question_from_chunks(
    question: str,
    chunks: List[Dict],
) -> str:
    """111
    Generate an answer to a question using only the provided chunks as context.

    Args:
        question: The user's question
        chunks: List of chunk dicts with keys: chunk_id, chunk_index, text, score

    Returns:
        A string answer based on the chunks
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

    elif llm_mode == "openai":
        # Call the OpenAI chat completion API with the chunks as context
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set for OpenAI LLM_MODE")
        openai.api_key = api_key

        model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

        if not chunks:
            # Still return a reasonable reply if there is no context
            prompt = f"Answer this question based on the available transcript context (none): {question}"
            messages = [
                {"role": "system", "content": "You are an assistant that only uses provided context to answer."},
                {"role": "user", "content": prompt},
            ]
        else:
            context = "\n\n".join([f"Chunk {c['chunk_index']}: {c['text']}" for c in chunks])
            messages = [
                {"role": "system", "content": "You are a helpful assistant that answers questions using only the provided transcript context. Do not make up facts."},
                {"role": "user", "content": f"Question: {question}\n\nContext:\n{context}"},
            ]

        response = openai.ChatCompletion.create(model=model_name, messages=messages)
        # return content from the first choice
        return response.choices[0].message.content

    else:
        raise ValueError(f"Invalid LLM_MODE: {llm_mode}. Must be 'stub' or 'openai'")
