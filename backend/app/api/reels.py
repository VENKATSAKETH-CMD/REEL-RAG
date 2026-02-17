"""FastAPI reels router
- POST /reels: multipart upload (file, title) -> {id, user_id, video_url, title, status, created_at}
- GET /reels: list reels with pagination -> [{...}, ...]
- GET /reels/{reel_id}: fetch single reel -> {...}
"""
from typing import List, Optional
import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status, BackgroundTasks
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.reel import Reel
from app.models.user import User
from app.api.auth import get_current_user
from app.services.storage import save_upload
from app.workers.tasks import transcribe_and_index_reel
from app.services.rag import answer_reel_question
from app.schemas.reels import ReelChatRequest, ReelChatResponse

# Import the helper function to convert paths to HTTP URLs
from app.utils import get_public_video_url

router = APIRouter()


@router.post("/reels", response_model=dict)
async def upload_reel(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a new reel video owned by the current authenticated user.
    - file: video file (required)
    - title: optional title
    Returns: Reel record with status="uploaded"
    """
    # Save file to storage
    # Create a deterministic/random filename for upload - keep original extension
    ext = Path(file.filename or "").suffix
    dest_filename = f"{uuid.uuid4().hex}{ext}"
    video_path = await save_upload(file, dest_filename)

    # Create Reel record owned by the logged-in user
    reel = Reel(
        user_id=current_user.id,
        video_url=video_path,
        title=title,
        status="uploaded",
    )

    session.add(reel)
    session.commit()
    session.refresh(reel)

    # Run transcribe/index worker asynchronously
    background_tasks.add_task(transcribe_and_index_reel, reel.id)

    # Refresh reel to get updated status from worker
    session.refresh(reel)

    return {
        "id": reel.id,
        "user_id": reel.user_id,
        "video_url": get_public_video_url(reel.video_url),
        "title": reel.title,
        "status": reel.status,
        "created_at": reel.created_at,
    }


@router.post("/reels/{reel_id}/chat", response_model=ReelChatResponse)
async def chat_reel(
    reel_id: int,
    payload: ReelChatRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    """
    Answer a question about a reel using RAG (Retrieval-Augmented Generation).
    
    Hardened for reliability:
    - Validates input message length
    - Checks reel exists and belongs to user
    - Ensures reel is ready before processing
    - Handles all exceptions gracefully with safe fallback responses
    - Never crashes; always returns a valid response or clear error
    
    Args:
        reel_id: ID of the reel to ask about
        payload: ChatRequest with 'message' field (string, max 2000 chars)
        session: Database session
        current_user: Authenticated user
    
    Returns:
        ChatResponse with 'answer' field (string)
    
    Raises:
        HTTPException: For validation failures (404, 403, 400)
    """
    # --- VALIDATION ---
    
    # 1. Validate message length
    MAX_MESSAGE_LENGTH = 2000
    message = payload.message.strip()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty"
        )
    
    if len(message) > MAX_MESSAGE_LENGTH:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Message exceeds maximum length of {MAX_MESSAGE_LENGTH} characters"
        )
    
    # 2. Load the reel
    reel = session.get(Reel, reel_id)
    if not reel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reel not found"
        )
    
    # 3. Access control: owner only
    if reel.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this reel"
        )
    
    # 4. Check reel is ready
    if reel.status == "uploaded":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reel is queued for processing. Try again in a few moments."
        )
    elif reel.status == "processing":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reel is still being processed. Try again in a few moments."
        )
    elif reel.status == "failed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reel failed to process. Please try uploading again."
        )
    elif reel.status != "ready":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Reel is not ready (status: {reel.status}). Try again later."
        )
    
    # --- ANSWER GENERATION (with graceful fallbacks) ---
    
    try:
        answer = answer_reel_question(session=session, reel=reel, user_message=message)
    except RuntimeError as e:
        # Configuration and API errors caught here
        error_msg = str(e)
        print(f"[CHAT] RuntimeError for reel {reel_id}: {error_msg}")
        
        # Map specific error types to user-safe messages
        if "OPENAI_API_KEY" in error_msg:
            answer = "Chat is temporarily unavailable due to missing API configuration. Please contact support."
        elif "rate limited" in error_msg.lower() or "quota exceeded" in error_msg.lower():
            answer = "AI responses are temporarily limited. Please try again in a few moments."
        elif "authentication failed" in error_msg.lower() or "api key" in error_msg.lower():
            answer = "Chat authentication error. Please contact support."
        elif "model not found" in error_msg.lower():
            answer = "AI model is currently unavailable. Please try again later."
        elif "PostgreSQL" in error_msg or "pgvector" in error_msg:
            answer = "Chat requires a properly configured database. Please contact support."
        else:
            # Generic fallback for other RuntimeErrors
            answer = "I encountered an issue while processing your question. Please try again later."
    except Exception as e:
        # Unexpected errors during RAG retrieval or generation
        # Log but return safe fallback instead of crashing
        print(f"[CHAT] Unexpected error for reel {reel_id}: {type(e).__name__}: {e}")
        answer = "I encountered an unexpected error while processing your question. Please try again later."
    
    return ReelChatResponse(answer=answer)


@router.get("/reels", response_model=List[dict])
def list_reels(
    page: int = 1,
    per_page: int = 20,
    session: Session = Depends(get_session),
):
    """
    List all reels with pagination.
    - page: 1-indexed page number
    - per_page: results per page
    Returns: List of Reel records ordered by created_at desc
    """
    offset = (page - 1) * per_page
    statement = (
        select(Reel)
        .offset(offset)
        .limit(per_page)
        .order_by(Reel.created_at.desc())
    )
    results = session.exec(statement).all()

    return [
        {
            "id": r.id,
            "user_id": r.user_id,
            "video_url": get_public_video_url(r.video_url),
            "title": r.title,
            "status": r.status,
            "created_at": r.created_at,
        }
        for r in results
    ]


@router.get("/reels/{reel_id}", response_model=dict)
def get_reel(
    reel_id: int,
    session: Session = Depends(get_session),
):
    """
    Fetch a single reel by ID.
    Returns: Reel record or 404 if not found
    """
    reel = session.get(Reel, reel_id)
    if not reel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reel not found",
        )

    return {
        "id": reel.id,
        "user_id": reel.user_id,
        "video_url": get_public_video_url(reel.video_url),
        "title": reel.title,
        "status": reel.status,
        "created_at": reel.created_at,
    }

