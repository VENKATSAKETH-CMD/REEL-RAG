"""
Reel RAG FastAPI Backend

Core application setup:
- Database initialization with pgvector for vector search
- JWT authentication routers
- Reel upload and chat endpoints
- Startup validation to fail fast on misconfiguration

REQUIREMENTS:
- PostgreSQL database with pgvector extension
- Environment variables in .env (see .env.example)
"""


import os
import sys
import uuid
import time
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables early
load_dotenv()

from fastapi import FastAPI, Request, Response
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel
from sqlalchemy import text

from app.db.session import engine, init_db, DATABASE_URL
from app.api import auth, reels


# ============================================================================
# STARTUP VALIDATION
# ============================================================================

def validate_environment() -> None:
    """
    Validate configuration on startup.
    Fail FAST and LOUD if required services are not configured.
    
    This prevents the app from starting in a broken state where users
    can upload videos but processing will fail.
    """
    errors = []
    warnings = []
    
    # ---- DATABASE ----
    if not DATABASE_URL:
        errors.append("DATABASE_URL not set. See .env.example for instructions.")
    elif not (DATABASE_URL.startswith("postgresql") or DATABASE_URL.startswith("postgres")):
        errors.append(
            f"DATABASE_URL must use PostgreSQL, not {DATABASE_URL.split(':')[0]}.\n"
            "RAG features require pgvector. Set DATABASE_URL to a PostgreSQL database.\n"
            "See .env.example for format."
        )
    
    # ---- EMBEDDINGS ----
    embed_mode = os.getenv("EMBED_MODE", "stub").lower()
    if embed_mode not in ["stub"]:
        errors.append(f"Invalid EMBED_MODE: '{embed_mode}'. Must be 'stub'.")
    
    # ---- ASR ----
    asr_mode = os.getenv("ASR_MODE", "stub").lower()
    if asr_mode not in ["stub"]:
        errors.append(f"Invalid ASR_MODE: '{asr_mode}'. Must be 'stub'.")
    
    # ---- STORAGE ----
    storage_path = os.getenv("STORAGE_LOCAL_PATH", "./data/uploads")
    try:
        os.makedirs(storage_path, exist_ok=True)
    except Exception as e:
        errors.append(f"Cannot create storage directory {storage_path}: {e}")
    
    # ---- JWT ----
    secret_key = os.getenv("SECRET_KEY", None)
    if not secret_key or secret_key == "dev-secret-key-change-me":
        if os.getenv("ENVIRONMENT") == "production":
            errors.append(
                "SECRET_KEY must be set for production. Generate one with:\n"
                "python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )
        else:
            warnings.append("⚠️  SECRET_KEY is using default value. Change it for production!")
    
    # ---- EMBEDDINGS DIMENSION ----
    try:
        embed_dim = int(os.getenv("EMBED_DIM", "1536"))
    except ValueError:
        errors.append("EMBED_DIM must be an integer (e.g., 1536)")
    
    # Report errors and warnings
    if errors:
        print("\n" + "="*80)
        print("❌ STARTUP VALIDATION FAILED")
        print("="*80)
        for i, error in enumerate(errors, 1):
            print(f"\n{i}. {error}")
        print("\n" + "="*80)
        print("Fix the configuration above and restart the server.")
        print("See .env.example for proper configuration.")
        print("="*80 + "\n")
        sys.exit(1)
    
    if warnings:
        print("\n" + "="*80)
        print("⚠️  WARNINGS")
        print("="*80)
        for warning in warnings:
            print(f"  {warning}")
        print("="*80 + "\n")


def validate_database() -> None:
    """
    Validate database connectivity and required extensions.
    Called after SQLModel creates tables.
    """
    try:
        with engine.connect() as conn:
            # Test basic connectivity
            conn.execute(text("SELECT 1"))
            
            # Ensure pgvector extension exists
            if DATABASE_URL.startswith(("postgres", "postgresql")):
                try:
                    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                    conn.commit()
                    print("✓ pgvector extension ready")
                except Exception as e:
                    print(f"⚠️  Warning: Could not verify pgvector extension: {e}")
                    print("   RAG features require pgvector. Ensure it's installed on your PostgreSQL server:")
                    print("   https://github.com/pgvector/pgvector")
    except Exception as e:
        print(f"\n❌ Database connection failed: {e}")
        print(f"DATABASE_URL: {DATABASE_URL}")
        print("\nEnsure PostgreSQL is running and DATABASE_URL is correct.")
        sys.exit(1)


# ============================================================================
# APP INITIALIZATION
# ============================================================================

app = FastAPI(
    title="Reel RAG API",
    version="0.1.0",
    description="Per-reel RAG with JWT authentication",
)

# =========================
# STRUCTURED LOGGING MIDDLEWARE
# =========================
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    response: Response = await call_next(request)
    duration_ms = int((time.time() - start_time) * 1000)
    log_data = {
        "request_id": request_id,
        "path": request.url.path,
        "method": request.method,
        "status_code": response.status_code,
        "duration_ms": duration_ms
    }
    print(f"[REQUEST] {log_data}")
    return response

# ============================================================================
# CORS MIDDLEWARE
# ============================================================================
# Configure CORS based on environment
# Development: Allow localhost dev servers
# Production: Use ALLOWED_ORIGINS env variable (comma-separated)
_default_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]
_allowed_origins = os.getenv("ALLOWED_ORIGINS", None)
if _allowed_origins:
    # Production: use env variable (e.g., "https://app.com,https://www.app.com")
    allowed_origins = [origin.strip() for origin in _allowed_origins.split(",")]
else:
    # Development: use defaults
    allowed_origins = _default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# STATIC FILES FOR VIDEO UPLOADS
# ============================================================================
# Expose the uploads directory as publicly accessible files
# Videos stored at ./data/uploads/abc123.mp4 will be accessible at /uploads/abc123.mp4
storage_path = os.getenv("STORAGE_LOCAL_PATH", "./data/uploads")
try:
    app.mount("/uploads", StaticFiles(directory=storage_path), name="uploads")
except Exception as e:
    print(f"⚠️  Warning: Could not mount static files from {storage_path}: {e}")
    print("   Videos may not be accessible via HTTP URLs.")


@app.on_event("startup")
def on_startup() -> None:
    """
    Initialize the application on startup.
    1. Validate configuration
    2. Initialize database
    3. Verify database connectivity
    """
    print("\n" + "="*80)
    print("Starting Reel RAG Backend...")
    print("="*80 + "\n")
    
    # Step 1: Validate environment before doing anything else
    validate_environment()
    
    # Step 2: Create all SQLModel tables
    print("Initializing database...")
    init_db()
    print("✓ Database tables initialized")
    
    # Step 3: Verify database is actually working
    validate_database()
    
    print("\n✅ Startup complete - server is ready\n")


# ============================================================================
# OPENAPI SCHEMA
# ============================================================================

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


# ============================================================================
# ROUTERS
# ============================================================================

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(reels.router, tags=["reels"])


# ============================================================================
# HEALTH CHECK
# ============================================================================


@app.get("/health")
def health_check():
    """
    Health check endpoint for monitoring.
    Checks:
      - DB connectivity
      - pgvector extension
      - OpenAI API reachability
    Returns JSON with status per service.
    """
    db_status = "unknown"
    pgvector_status = "unknown"
    openai_status = "unknown"
    # DB connectivity
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_status = "ok"
            # pgvector extension check
            try:
                res = conn.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector'"))
                if res.fetchone():
                    pgvector_status = "ok"
                else:
                    pgvector_status = "missing"
            except Exception as e:
                pgvector_status = f"error: {str(e)[:50]}"
    except Exception as e:
        db_status = f"error: {str(e)[:50]}"
        pgvector_status = "skipped"

    # OpenAI API check
    try:
        from app.services.embeddings import openai as openai_client
        api_key = os.getenv("OPENAI_API_KEY")
        if openai_client and api_key:
            openai_client.api_key = api_key
            # Use a lightweight endpoint (models.list)
            openai_client.models.list()
            openai_status = "ok"
        elif not api_key:
            openai_status = "missing_api_key"
        else:
            openai_status = "not_installed"
    except Exception as e:
        openai_status = f"error: {str(e)[:50]}"

    return {
        "database": db_status,
        "pgvector": pgvector_status,
        "openai": openai_status,
        "status": "ok" if db_status == "ok" and pgvector_status == "ok" and openai_status == "ok" else "degraded"
    }

