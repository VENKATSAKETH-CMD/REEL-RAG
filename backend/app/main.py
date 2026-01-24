
"""
Phase 1 FastAPI app for Reel RAG.

WHAT:
- Create the FastAPI application instance.
- Include routers for auth and reels under appropriate prefixes.
- Initialize the database on startup.

WHY:
- This is the entrypoint for uvicorn.
- Future phases will add:
  - Chat router for POST /reels/{id}/chat
  - Health check, maybe docs customization, etc.

HOW:
- Create a FastAPI app with a descriptive title and version.
- Import and include:
  - auth_router with prefix="/auth"
  - reels_router with prefix="/reels"
- On startup event:
  - Call init_db(engine) from db.base using the engine from db.session.
"""

# TODO: FastAPI app initializer
# - create SQLModel tables on startup
# - include auth and reels routers
# - expose health check endpoint
print("🔥 USING MAIN.PY FROM:", __file__)

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from sqlmodel import SQLModel
from sqlalchemy import text

from app.db.session import engine, init_db
from app.api import auth, reels
from app.db.session import DATABASE_URL

app = FastAPI(
    title="Reel RAG API",
    version="0.1.0",
    description="Per-reel RAG with JWT authentication",
)


@app.on_event("startup")
def on_startup() -> None:
    # Ensure pgvector extension exists if using Postgres
    from app.db.session import DATABASE_URL
    if DATABASE_URL.startswith("postgres") or DATABASE_URL.startswith("postgresql"):
        try:
            with engine.connect() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.commit()  # Ensure the extension is created
        except Exception as e:
            raise RuntimeError(f"Failed to create pgvector extension: {e}. Ensure PostgreSQL has pgvector installed.")

    # Initialize the DB (create tables, etc.)
    init_db()

    # Warn if using SQLite: RAG requires Postgres + pgvector
    if DATABASE_URL.startswith("sqlite"):
        print("⚠️  Warning: DATABASE_URL uses sqlite. RAG features require Postgres+pgvector. Set DATABASE_URL to PostgreSQL for RAG to work.")


def custom_openapi():
    """Register OAuth2 security scheme in OpenAPI (makes Authorize button appear)."""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Reel RAG API",
        version="0.1.0",
        description="Per-reel RAG with JWT authentication",
        routes=app.routes,
    )
    
    # Register Bearer/JWT security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(reels.router, tags=["reels"])


@app.get("/health")
def health_check():
    # Check DB connectivity
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {"status": "ok", "db": db_status}
