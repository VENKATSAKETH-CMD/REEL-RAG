"""
Import models so that SQLModel/SQLAlchemy registers them with the metadata
when `app.models` is imported. This ensures `SQLModel.metadata.create_all(...)`
includes all tables even when a script imports only a subset of model files.

This file centralizes the imports and avoids circular import problems because
it is safe to import model classes by name only (no runtime logic).
"""
from .user import User  # noqa: F401
from .reel import Reel  # noqa: F401
from .transcript import ReelTranscript  # noqa: F401
from .chunk import ReelChunk  # noqa: F401
