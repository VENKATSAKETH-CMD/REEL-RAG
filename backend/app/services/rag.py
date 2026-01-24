"""
Phase 3 — RAG (Retrieval-Augmented Generation) Service

Handles semantic search and chunk retrieval for a reel based on question embeddings.
"""

import json
import math
from typing import List, Dict

from sqlmodel import Session, select
from sqlalchemy import text, func

from app.db.session import engine, DATABASE_URL
from app.models.reel import Reel


def ensure_postgres_for_rag() -> None:
    if not (DATABASE_URL.startswith("postgres") or DATABASE_URL.startswith("postgresql")):
        raise RuntimeError("RAG features require PostgreSQL with pgvector. DATABASE_URL must point to PostgreSQL.")
from app.models.chunk import ReelChunk
from app.services.embeddings import embed_text
# We no longer use `answer_question_from_chunks` in this file (we call OpenAI directly).
# We will use raw SQL `text()` for the pgvector operator rather than relying
# on SQLAlchemy `func` wrappers that might not exist for pgvector in all
# package versions.
from openai import OpenAI
import os


def _cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    Args:
        vec_a: First vector
        vec_b: Second vector

    Returns:
        Cosine similarity score (float between -1 and 1, typically 0 to 1 for embeddings)
    """
    if len(vec_a) != len(vec_b):
        raise ValueError("Vectors must have the same length")

    # Compute dot product
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))

    # Compute magnitudes
    mag_a = math.sqrt(sum(a * a for a in vec_a))
    mag_b = math.sqrt(sum(b * b for b in vec_b))

    if mag_a == 0 or mag_b == 0:
        return 0.0

    return dot_product / (mag_a * mag_b)


def retrieve_chunks_for_question(
    reel_id: int,
    question: str,
    top_k: int = 5,
) -> List[Dict]:
    """
    Retrieve the most relevant chunks for a question using cosine similarity.

    Args:
        reel_id: ID of the reel
        question: The question to find relevant chunks for
        top_k: Number of top chunks to return (default: 5)

    Returns:
        List of dicts with keys: chunk_id, chunk_index, text, score
        Sorted by score in descending order
    """
    # Enforce Postgres + pgvector for RAG search — no SQLite fallback
    if not (DATABASE_URL.startswith("postgres") or DATABASE_URL.startswith("postgresql")):
        raise RuntimeError("RAG retrieval requires PostgreSQL with pgvector enabled; set DATABASE_URL accordingly")

    question_vector = embed_text(question)

    # Postgres + pgvector usage: query nearest neighbors using the `<->` operator
    table_name = ReelChunk.__table__.name
    vec_literal = "[" + ",".join(str(x) for x in question_vector) + "]"
    sql = text(
        f"SELECT id, chunk_index, text, (embedding <-> :vec::vector) AS dist "
        f"FROM {table_name} WHERE reel_id = :rid ORDER BY dist ASC LIMIT :k"
    )
    with engine.connect() as conn:
        rows = conn.execute(sql, {"vec": vec_literal, "rid": reel_id, "k": top_k}).all()
    if not rows:
        return []
    chunk_scores = []
    for row in rows:
        dist = row["dist"] if "dist" in row.keys() else row[3]
        # Convert distance into a similarity-like score (higher is better)
        score = 1.0 / (1.0 + float(dist))
        chunk_scores.append(
            {
                "chunk_id": row["id"],
                "chunk_index": row["chunk_index"],
                "text": row["text"],
                "score": score,
            }
        )
    return chunk_scores


def search_reel_chunks_pgvector(
    session: Session,
    reel_id: int,
    query_embedding: List[float],
    top_k: int = 5,
) -> List[ReelChunk]:
    """
    Search for relevant ReelChunk objects using pgvector cosine distance.
    Returns a list of ReelChunk objects ordered by similarity (nearest first) up to top_k.
    """
    # Compose a textual vector literal like "[0.1,0.2,...]" and pass it as a
    # parameter cast to `vector` in the SQL function call. Using `func` lets us
    # call `cosine_distance()` using SQLAlchemy without importing a package
    # specific wrapper. (The `func.cosine_distance` call compiles to
    # `cosine_distance(embedding, :vec::vector)` in SQL.)
    vec_literal = "[" + ",".join(str(float(x)) for x in query_embedding) + "]"
    stmt = (
        select(ReelChunk)
        .where(ReelChunk.reel_id == reel_id)
        .order_by(func.cosine_distance(ReelChunk.embedding, text(":vec::vector")))
        .limit(top_k)
    )
    # Parameterize the vector as `vec` and cast to the pgvector `vector` type.
    return session.exec(stmt, params={"vec": vec_literal}).all()



def answer_reel_question(session: Session, reel: Reel, user_message: str, top_k: int = 5) -> str:
    """
    High-level helper to retrieve chunks for a reel and answer a question using the LLM helper.
    Returns a dict with keys: answer (str), chunks_used (list of chunks dicts)
    """
    ensure_postgres_for_rag()

    # Build an OpenAI client that will be used for both embedding & chat calls
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise RuntimeError("OPENAI_API_KEY not set for OpenAI usage in answer_reel_question")
    client = OpenAI(api_key=openai_api_key)

    # 1) Compute embedding for the user question using the same model as the worker
    emb_resp = client.embeddings.create(model="text-embedding-3-small", input=[user_message])
    query_embedding = emb_resp.data[0].embedding

    # 2) Retrieve similar chunks (use pgvector search helper)
    chunks = search_reel_chunks_pgvector(session=session, reel_id=reel.id, query_embedding=query_embedding, top_k=top_k)

    # 3) Build context text using returned chunks
    if chunks:
        context_parts = [c.text.strip() for c in chunks if c.text]
        context_text = "\n\n---\n\n".join(context_parts)
    else:
        context_text = "No transcript context was found for this reel."

    # 4) Call OpenAI chat model and return a final string answer
    system_prompt = (
        "You are an assistant that answers questions about a short video (reel) "
        "using ONLY the provided transcript context. If the answer is not clearly "
        "in the context, say you don't know."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": (
                f"Here is the transcript context from the reel:\n\n{context_text}\n\n"
                f"User question: {user_message}"
            ),
        },
    ]

    completion = client.chat.completions.create(model="gpt-4o-mini", messages=messages, temperature=0.2)
    return completion.choices[0].message.content.strip()
