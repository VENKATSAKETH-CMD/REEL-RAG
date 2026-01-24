from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.reel import Reel


class ReelTranscript(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    reel_id: int = Field(foreign_key="reel.id")
    full_text: str
    created_at: datetime = Field(default_factory=datetime.now)

    # Relationship back to Reel
    reel: Optional["Reel"] = Relationship(back_populates="transcript")
