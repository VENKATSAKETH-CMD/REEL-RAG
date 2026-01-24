from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
	from app.models.reel import Reel


class User(SQLModel, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	email: str = Field(index=True, sa_column_kwargs={"unique": True})
	password_hash: str
	created_at: datetime = Field(default_factory=datetime.utcnow)

	# Relationship back to reels
	reels: List["Reel"] = Relationship(back_populates="user")


