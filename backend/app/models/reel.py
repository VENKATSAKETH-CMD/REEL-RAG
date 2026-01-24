# Phase 2 – Hook upload into background processing (Copilot instructions)
# Update the upload_reel endpoint to:
#   - Accept a BackgroundTasks parameter from fastapi.
#   - After creating and committing the Reel object,
#     schedule the worker:
#         background_tasks.add_task(transcribe_and_index_reel, reel.id)
#
# Requirements:
#   - Import:
#       from fastapi import BackgroundTasks
#       from app.workers.tasks import transcribe_and_index_reel
#   - Function signature should look like:
#
#       async def upload_reel(
#           file: UploadFile = File(...),
#           title: Optional[str] = Form(None),
#           session: Session = Depends(get_session),
#           current_user: User = Depends(get_current_user),
#           background_tasks: BackgroundTasks,
#       ):
#
#   - After saving the file and creating Reel, do:
#         background_tasks.add_task(transcribe_and_index_reel, reel.id)
#
#   - Response body can stay the same, but reel.status will initially be "uploaded"
#     and later changed to "processing" then "ready"/"failed" by the worker.

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.transcript import ReelTranscript
    from app.models.chunk import ReelChunk
    from app.models.user import User


class Reel(SQLModel, table=True):
    # Core columns used by the codebase
    id: Optional[int] = Field(default=None, primary_key=True)
    # User foreign key if user model exists
    user_id: int = Field(foreign_key="user.id", index=True)
    title: Optional[str] = Field(default=None)
    video_url: str
    status: str = Field(default="uploaded", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="reels")
    transcript: Optional["ReelTranscript"] = Relationship(back_populates="reel")
    chunks: List["ReelChunk"] = Relationship(back_populates="reel")
