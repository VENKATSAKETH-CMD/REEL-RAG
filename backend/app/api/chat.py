"""FastAPI chat router for per-reel RAG chat."""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session

from app.db.session import get_session
from app.models.reel import Reel
from app.models.user import User
from app.api.auth import get_current_user
from app.services.rag import answer_reel_question


class ChatRequest(BaseModel):
    """Request body for chat endpoint."""

    question: str


class ChunkInfo(BaseModel):
    """Information about a chunk used in the answer."""

    chunk_id: int
    chunk_index: int
    text: str
    score: float


class ChatResponse(BaseModel):
    """Response body for chat endpoint."""

    answer: str
    chunks_used: List[ChunkInfo]


router = APIRouter()

# NOTE: We removed the router's chat endpoint because the `reels` router implements
# chat functionality under the same path to keep the API centralized. This file now
# only contains types that other modules could import if needed.
