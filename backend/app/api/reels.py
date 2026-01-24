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

router = APIRouter()


# `ReelChatRequest` and `ReelChatResponse` are defined in `app.schemas.reels`


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
        "video_url": reel.video_url,
        "title": reel.title,
        "status": reel.status,
        "created_at": reel.created_at,
    }


@router.post("/reels/{reel_id}/chat", response_model=ReelChatResponse)
def chat_reel(
    reel_id: int,
    payload: ReelChatRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # 1. Load the reel
    reel = session.get(Reel, reel_id)
    if not reel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reel not found")

    # 2. Access control: owner only
    if reel.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this reel")

    # 3. Check status
    if reel.status != "ready":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reel is not ready for chat yet. Try again later.")

    # 4. Answer question
    try:
        answer = answer_reel_question(session=session, reel=reel, user_message=payload.message)
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))

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
            "video_url": r.video_url,
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
        "video_url": reel.video_url,
        "title": reel.title,
        "status": reel.status,
        "created_at": reel.created_at,
    }

