# Reel RAG Backend - Setup & Testing Guide

## Overview

This backend implements a **Retrieval-Augmented Generation (RAG)** system for video reels:

1. **Upload** a video
2. **Process** it in the background (transcribe + embed chunks)
3. **Chat** about the video using semantic search

**Status**: MVP with stub implementations (no external API calls required for demo)

---

## Quick Start (5 minutes)

### Prerequisites

- **Python 3.9+**
- **PostgreSQL 12+** with [pgvector](https://github.com/pgvector/pgvector) extension
- **pip** (Python package manager)

### Installation

1. **Clone and navigate to backend:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and set:
   ```
   DATABASE_URL=postgresql://postgres:password@localhost:5432/reel_rag_dev
   SECRET_KEY=your-random-secret-key-here
   ```

5. **Create PostgreSQL database:**
   ```bash
   # Using psql command-line:
   createdb reel_rag_dev
   
   # OR using PostgreSQL admin tools
   ```

6. **Install pgvector extension (one-time):**
   ```bash
   psql reel_rag_dev -c "CREATE EXTENSION IF NOT EXISTS vector;"
   ```

7. **Start the server:**
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   You should see:
   ```
   ✅ Startup complete - server is ready
   ```

8. **Verify it's working:**
   ```bash
   curl http://localhost:8000/health
   # Expected: {"status": "ok", "database": "ok"}
   ```

---

## Testing End-to-End

### Option A: Automated Test Script

```bash
python test_integration.py
```

This script will:
- ✅ Register a test user
- ✅ Upload a test video
- ✅ Wait for processing
- ✅ Ask a question and get an answer

### Option B: Manual Testing with curl

**Step 1: Register**
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'

# Save the response (we'll use email/password next)
```

**Step 2: Login**
```bash
curl -X POST http://localhost:8000/auth/login \
  -d "username=user@example.com" \
  -d "password=password123"

# Response: {"access_token": "...", "token_type": "bearer"}
# Save the access_token as TOKEN
TOKEN="eyJ0eXAi..."
```

**Step 3: Upload Video**
```bash
# Create a small test video:
dd if=/dev/zero of=test.mp4 bs=1M count=1

# Upload it:
curl -X POST http://localhost:8000/reels \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test.mp4" \
  -F "title=Test Video"

# Save the returned reel_id
# Response: {"id": 1, "status": "uploaded", ...}
```

**Step 4: Check Processing Status**
```bash
# Wait a few seconds (default: stub transcription is instant)
sleep 3

curl -X GET http://localhost:8000/reels/1 \
  -H "Authorization: Bearer $TOKEN"

# Check status field: uploaded -> processing -> ready
```

**Step 5: Ask Questions**
```bash
# Once status is "ready":
curl -X POST http://localhost:8000/reels/1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What was discussed in the video?"
  }'

# Response: {"answer": "Based on the transcript..."}
```

### Option C: Use Swagger UI

1. Open http://localhost:8000/docs in your browser
2. Click "Authorize" button (top right)
3. Get a token via `/auth/login` endpoint
4. Use the token to test other endpoints interactively

---

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────┐
│ Frontend (React, see ../frontend)                       │
└──────────────┬──────────────────────────────────────────┘
               │ HTTP API
               ▼
┌─────────────────────────────────────────────────────────┐
│ FastAPI Backend (this directory)                        │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ API Routers                                     │   │
│  │  - /auth/* (register, login)                   │   │
│  │  - /reels/* (upload, list, chat)               │   │
│  └─────────────────────────────────────────────────┘   │
│                      │                                  │
│  ┌────────────────────▼──────────────────────────┐     │
│  │ RAG Services (Retrieval-Augmented Generation) │     │
│  │  - embeddings.py (stub vectors)               │     │
│  │  - rag.py (semantic search + chat)            │     │
│  │  - asr.py (transcription service)             │     │
│  └────────────────────┬──────────────────────────┘     │
│                       │                                │
│  ┌────────────────────▼──────────────────────────┐     │
│  │ Background Worker                             │     │
│  │  - tasks.py (transcribe + index)              │     │
│  └────────────────────┬──────────────────────────┘     │
│                       │                                │
└───────────────────────┼────────────────────────────────┘
                        │
        ┌───────────────┴───────────────┐
        ▼                               ▼
    ┌─────────────┐           ┌─────────────────┐
    │ PostgreSQL  │           │ File Storage    │
    │ + pgvector  │           │ ./data/uploads/ │
    └─────────────┘           └─────────────────┘
```

### Data Flow

1. **Upload**: User uploads video → FastAPI saves to disk → Background worker triggered
2. **Process**: Worker transcribes video → Chunks text → Embeds chunks → Saves to DB
3. **Chat**: User asks question → Embed question → Vector search → Retrieve chunks → LLM generates answer

### Key Design Decisions

| Aspect | Choice | Why |
|--------|--------|-----|
| **Embeddings** | Stub (deterministic) | No API calls needed; consistent for demos |
| **Transcription** | Stub | No external services; fast testing |
| **Chat LLM** | OpenAI GPT-4o-mini | Best cost/quality; can be swapped later |
| **Vector DB** | PostgreSQL + pgvector | Open-source, no vendor lock-in |
| **Background Jobs** | Synchronous (FastAPI BackgroundTasks) | Simple; works for MVP; scale with Celery later |

---

## Configuration

See `.env.example` for all options. Key variables:

```bash
# Database (REQUIRED)
DATABASE_URL=postgresql://user:pass@localhost:5432/db

# Authentication
SECRET_KEY=...                          # Change this!
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Embeddings (currently only "stub" works)
EMBED_MODE=stub
EMBED_DIM=1536

# Transcription (currently only "stub" works)
ASR_MODE=stub

# Optional: for future OpenAI integration
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

---

## File Structure

```
backend/
├── app/
│   ├── main.py                  # FastAPI app + startup validation
│   ├── api/
│   │   ├── auth.py              # User registration & login
│   │   ├── chat.py              # (deprecated - types only)
│   │   └── reels.py             # Reel upload, list, chat
│   ├── services/
│   │   ├── embeddings.py        # Single source of truth for embeddings
│   │   ├── rag.py               # Semantic search + answer generation
│   │   ├── asr.py               # Speech-to-text
│   │   ├── storage.py           # File storage
│   │   └── llm.py               # (deprecated - kept for reference)
│   ├── models/
│   │   ├── user.py              # User table
│   │   ├── reel.py              # Reel table + relationships
│   │   ├── chunk.py             # ReelChunk (vectors) + chunking logic
│   │   └── transcript.py        # ReelTranscript table
│   ├── schemas/
│   │   └── reels.py             # Request/response Pydantic models
│   ├── db/
│   │   └── session.py           # Database connection + init
│   └── workers/
│       └── tasks.py             # Background transcription worker
├── .env.example                 # Configuration template
├── requirements.txt             # Python dependencies
├── test_integration.py          # End-to-end test script
└── README.md                    # This file
```

---

## Troubleshooting

### Error: "PostgreSQL + pgvector required"
- Ensure `DATABASE_URL` points to PostgreSQL (not SQLite)
- Ensure pgvector extension is installed:
  ```bash
  psql $DATABASE_URL -c "CREATE EXTENSION IF NOT EXISTS vector;"
  ```

### Error: "Database connection failed"
- Check PostgreSQL is running: `psql -U postgres`
- Check DATABASE_URL format: `postgresql://user:pass@host:port/dbname`
- Try connecting manually: `psql $DATABASE_URL`

### Reel stuck in "processing"
- Check logs: `curl http://localhost:8000/reels/{id}`
- If status is "processing" for >30s, something failed silently
- Restart worker: restart FastAPI server
- Check `.env` values (EMBED_DIM, EMBED_MODE, etc.)

### Chat returns "I don't know"
- Ensure reel status is "ready" (not "processing" or "failed")
- Check video was actually uploaded (has file content)
- In stub mode, transcription is deterministic; long questions might not find context
- Try asking a simpler question

### Port 8000 already in use
```bash
# Kill the process:
lsof -i :8000
kill -9 <PID>

# Or use a different port:
python -m uvicorn app.main:app --port 8001
```

---

## Performance Notes

- **Stub transcription**: <100ms (instant)
- **Stub embeddings**: <1ms per chunk
- **Vector search**: <100ms (depends on chunk count)
- **LLM chat**: 1-5s (OpenAI API latency)

For **production**:
- Use a task queue (Celery) instead of BackgroundTasks
- Add caching for frequent queries
- Use connection pooling for PostgreSQL
- Implement rate limiting on uploads

---

## Next Steps

- [ ] Add real transcription (OpenAI Whisper)
- [ ] Add real embeddings (OpenAI text-embedding-3-small)
- [ ] Improve chunking logic (sentence-aware)
- [ ] Add full test suite (pytest)
- [ ] Deploy to production (Docker, Kubernetes)
- [ ] Frontend integration

---

## Support

For issues:
1. Check logs: `python -m uvicorn app.main:app --reload` (shows startup errors)
2. Test health: `curl http://localhost:8000/health`
3. Try integration test: `python test_integration.py`
4. Check `.env` configuration against `.env.example`

---

**Version**: 0.1.0 | **Status**: MVP with stub implementations
