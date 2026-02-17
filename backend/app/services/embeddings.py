"""
Phase 2 — Embedding Service

Handles text-to-vector conversion for semantic search and similarity.

IMPORTANT: This is the SINGLE SOURCE OF TRUTH for embeddings.
Both background indexing (worker) and chat-time retrieval (RAG) MUST use
this function to ensure embedding consistency across the system.

Current implementation: STUB mode (deterministic, no API calls required)
- Workers use embed_text() during indexing
- RAG retrieval uses embed_text() during query time
- Both get the same deterministic vectors → matches across indexing & retrieval
"""


import os
import time
from typing import List, Union

try:
    import openai
except ImportError:
    openai = None

EMBED_DIM = int(os.getenv("EMBED_DIM", "1536"))



def embed_text(texts: Union[str, List[str]]) -> Union[List[float], List[List[float]]]:
    """
    Convert text(s) to embedding vector(s) using the configured backend.
    Accepts a single string or a list of strings. Returns a single vector or a list of vectors.

    Args:
        texts: Text or list of texts to embed

    Returns:
        List of floats (if input is str) or list of list of floats (if input is list)

    Raises:
        ValueError: If EMBED_MODE is invalid
    """
    embed_mode = os.getenv("EMBED_MODE", "stub").lower()

    if isinstance(texts, str):
        single = True
        texts_list = [texts]
    else:
        single = False
        texts_list = list(texts)

    if embed_mode == "stub":
        n = EMBED_DIM
        def stub_vec(t):
            base = (len(t) % 100) / 100.0
            return [base for _ in range(n)]
        result = [stub_vec(t) for t in texts_list]
        return result[0] if single else result

    elif embed_mode == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set. Cannot use OpenAI embeddings.")
        if openai is None:
            raise RuntimeError("openai package is not installed.")

        model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
        batch_size = 100
        all_vectors = []
        total_tokens = 0
        openai.api_key = api_key
        for i in range(0, len(texts_list), batch_size):
            batch = texts_list[i:i+batch_size]
            for attempt in range(3):
                try:
                    start = time.time()
                    response = openai.embeddings.create(
                        model=model,
                        input=batch
                    )
                    duration = time.time() - start
                    vectors = [d.embedding for d in response.data]
                    all_vectors.extend(vectors)
                    usage = getattr(response, "usage", None)
                    if usage:
                        tokens = usage.get("total_tokens") or usage.get("prompt_tokens")
                        if tokens:
                            total_tokens += tokens
                    print(f"[EMBED] Batch {i//batch_size+1}: {len(batch)} texts, {duration:.2f}s, tokens: {tokens if usage else 'n/a'}")
                    break
                except Exception as e:
                    if attempt == 2:
                        raise RuntimeError(f"OpenAI embedding API failed after 3 attempts: {e}")
                    time.sleep(1.5 * (attempt + 1))
        if total_tokens:
            print(f"[EMBED] Total tokens used: {total_tokens}")
        return all_vectors[0] if single else all_vectors

    else:
        raise ValueError(f"Invalid EMBED_MODE: '{embed_mode}'. Must be 'stub' or 'openai'.")
