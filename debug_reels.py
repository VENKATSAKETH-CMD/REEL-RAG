"""
Debug script for listing recent Reels from the project DB.

How to run:
    cd "/Users/venkat/Desktop/INSTA CLONE CHAT BOT /backend"
    python ../debug_reels.py

This script will try to reuse the project's DB session/engine if available
by trying to import `app.db.session.engine`. If not available, it falls back
to reading the DATABASE_URL environment variable (or `backend/.env`) and
creating a local SQLModel engine.

It prints the ten most recent Reel rows with: id, user_id, video_url, status, created_at
"""

import os
import sys
from pathlib import Path
from typing import Optional

# Ensure project root is on sys.path so imports work
PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_PATH = PROJECT_ROOT / "backend"
if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

# Try to import the project models and session helper
try:
    from app.models.reel import Reel
    from app.db.session import engine as project_engine
    from sqlmodel import Session, select
    engine = project_engine
    print("Using engine imported from app.db.session.engine")
except Exception as e:
    # Fall back to DATABASE_URL or look in backend/.env
    print("Could not import project engine (app.db.session.engine):", e)
    from sqlmodel import create_engine, Session, select

    DATABASE_URL = os.environ.get("DATABASE_URL")
    if not DATABASE_URL:
        # try to read the backend/.env file
        env_path = BACKEND_PATH / ".env"
        if env_path.exists():
            with open(env_path, "r") as f:
                for line in f:
                    if line.strip().startswith("DATABASE_URL="):
                        DATABASE_URL = line.strip().split("=", 1)[1]
                        break
    if not DATABASE_URL:
        print("No DATABASE_URL found in environment or backend/.env. Cannot continue.")
        sys.exit(1)

    print("Using fallback DATABASE_URL:", DATABASE_URL)
    engine = create_engine(DATABASE_URL, echo=False)

# Importing the model; if import fails, abort
try:
    from app.models.reel import Reel
except Exception as e:
    print("Failed to import Reel model:", e)
    print("Make sure the project's models are importable.")
    sys.exit(1)

# Query the top 10 recent reels and print
with Session(engine) as session:
    try:
        statement = select(Reel).order_by(Reel.id.desc()).limit(10)
        results = session.exec(statement).all()
    except Exception as e:
        print("Failed running query — perhaps the tables aren't set up or engine is invalid:", e)
        sys.exit(1)

if not results:
    print("No reels found (DB empty / tables not seeded).")
else:
    for r in results:
        print(
            f"Reel(id={r.id}, user_id={getattr(r, 'user_id', None)}, "
            f"video_url={getattr(r, 'video_url', None)!r}, status={getattr(r, 'status', None)!r}, "
            f"created_at={getattr(r, 'created_at', None)})"
        )

print("Done.")
