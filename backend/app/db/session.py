import os
from typing import Generator

from sqlmodel import SQLModel, Session, create_engine


# Read database URL from environment; default to local sqlite for dev
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")


def _create_engine(url: str):
	# Use SQLite connect args when appropriate
	if url.startswith("sqlite"):
		return create_engine(url, echo=False, connect_args={"check_same_thread": False})
	return create_engine(url, echo=False)


engine = _create_engine(DATABASE_URL)


def init_db() -> None:
	"""Create database tables for all SQLModel metadata.

	Call this once on startup to create tables if they don't exist.
	"""
	# Make sure all models are imported so SQLModel metadata contains them.
	# Importing the package triggers `app.models.__init__` which registers
	# all models defined in this application. This avoids `InvalidRequestError`
	# when SQLAlchemy tries to initialize mappers for relationships that are
	# defined across multiple modules.
	try:
		import app.models  # noqa: F401
	except Exception:
		# Import errors should be surfaced elsewhere, but we don't want DB init
		# to crash just due to import ordering during tests; continue and
		# attempt to create tables regardless.
		pass

	SQLModel.metadata.create_all(bind=engine)


def get_session() -> Generator[Session, None, None]:
	"""FastAPI dependency that yields a SQLModel Session.

	Usage:
		session: Session = Depends(get_session)
	"""
	with Session(engine) as session:
		yield session


