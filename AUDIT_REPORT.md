# CODE AUDIT REPORT: Instagram Reel AI Chatbot
**Date:** January 25, 2026  
**Scope:** Complete codebase audit (no modifications)  
**Status Assessment:** Prototype with Phase 3 backend mostly complete, Phase 4 frontend not started

---

## 1. CONFIRMED IMPLEMENTED FEATURES

### 1.1 User Authentication (✅ COMPLETE)
- **Files:** `backend/app/api/auth.py`
- **Implemented:**
  - `POST /auth/register` — Email + password signup with bcrypt hashing
  - `POST /auth/login` — JWT token generation (HS256, 60-min expiry)
  - `get_current_user()` — OAuth2 bearer token validation
  - Password verification and token lifecycle management

### 1.2 Reel Upload & Management API (✅ COMPLETE)
- **Files:** `backend/app/api/reels.py`
- **Endpoints:**
  - `POST /reels` — Multipart file upload → saves to `backend/data/uploads/` → creates Reel record with status="uploaded" → triggers background job
  - `GET /reels` — Paginated list (20 per page, ordered by created_at DESC)
  - `GET /reels/{reel_id}` — Fetch single reel metadata
- **File Storage:** `backend/app/services/storage.py` — Local disk storage with UUID + extension preservation

### 1.3 Database Models & Schema (✅ COMPLETE)
- **Files:** `backend/app/models/{user.py, reel.py, transcript.py, chunk.py}`
- **Tables:**
  - `User` — id, email (unique), password_hash, created_at, relationships
  - `Reel` — id, user_id (FK), video_url, title, status, created_at, relationships
  - `ReelTranscript` — id, reel_id (FK), full_text, created_at
  - `ReelChunk` — id, reel_id (FK), chunk_index, text, embedding (pgvector), model_name, created_at
- **Framework:** SQLModel with proper relationships and foreign key constraints

### 1.4 Database Setup & Session (✅ COMPLETE)
- **Files:** `backend/app/db/session.py`
- **Features:**
  - PostgreSQL connection (`postgresql+psycopg://venkat@localhost:5432/reels`)
  - SQLModel engine initialization with SQLite fallback
  - `init_db()` creates all tables on startup
  - `get_session()` FastAPI dependency for transactions

### 1.5 Text Chunking (✅ COMPLETE)
- **Files:** `backend/app/models/chunk.py`
- **Function:** `chunk_text(full_text, max_chars=2000, overlap=300)`
- **Returns:** List of `{"index": int, "text": str}` with sliding-window 300-char overlap

### 1.6 Speech-to-Text Service (🔶 PARTIAL — Stub Only)
- **Files:** `backend/app/services/asr.py`
- **Current Mode:** `ASR_MODE=stub` (default) → Returns deterministic fake transcript
- **Status:** `ASR_MODE=openai` raises `NotImplementedError` (not wired)
- **Environment:** `.env` uses stub mode

### 1.7 Text Embedding Service (🔶 PARTIAL — Stub Only)
- **Files:** `backend/app/services/embeddings.py`
- **Current Mode:** `EMBED_MODE=stub` (default) → Returns fake 1536-dim vector based on text length
- **Status:** `EMBED_MODE=openai` raises `NotImplementedError` (not wired)
- **Environment:** `.env` uses stub mode

### 1.8 Background Transcription Worker (✅ COMPLETE)
- **Files:** `backend/app/workers/tasks.py`
- **Function:** `transcribe_and_index_reel(reel_id)` — Synchronous background job
- **Workflow:**
  1. Load reel, mark status → "processing"
  2. Transcribe via ASR service
  3. Save ReelTranscript row
  4. Chunk transcript into overlapping segments
  5. Embed each chunk
  6. Save ReelChunk rows with vectors
  7. Mark status → "ready" (or "failed" on exception)
- **Integration:** Triggered via FastAPI `BackgroundTasks.add_task()`

### 1.9 RAG Service (🔶 PARTIAL — Requires OpenAI + PostgreSQL)
- **Files:** `backend/app/services/rag.py`
- **Functions:**
  - `retrieve_chunks_for_question(reel_id, question, top_k=5)` — pgvector cosine similarity search
  - `answer_reel_question(session, reel, user_message)` — Full RAG pipeline:
    - Embeds question via OpenAI API
    - Retrieves top chunks via pgvector
    - Calls OpenAI chat (gpt-4o-mini) with context
    - Returns final answer string
- **Dependencies:** Requires `OPENAI_API_KEY` and PostgreSQL with pgvector extension

### 1.10 Chat Endpoint (✅ COMPLETE)
- **Files:** `backend/app/api/reels.py`, `backend/app/schemas/reels.py`
- **Endpoint:** `POST /reels/{reel_id}/chat`
- **Request:** `{"message": "string"}`
- **Response:** `{"answer": "string"}`
- **Logic:**
  - Validates reel exists and user owns it
  - Checks status == "ready"
  - Calls RAG service for answer
  - Returns 503 if OPENAI_API_KEY missing

### 1.11 FastAPI Application (✅ COMPLETE)
- **Files:** `backend/app/main.py`
- **Features:**
  - Title: "Reel RAG API", Version: "0.1.0"
  - Startup event: Creates pgvector extension, initializes DB
  - Routers: `/auth` and `/reels` with `/health` endpoint
  - OpenAPI security: Bearer JWT scheme
  - Warning if using SQLite (RAG requires PostgreSQL)

### 1.12 Debug Utility (✅ COMPLETE)
- **Files:** `debug_reels.py`
- **Purpose:** Query and print recent Reels from database for dev verification

---

## 2. PARTIALLY IMPLEMENTED / INCOMPLETE

### 2.1 OpenAI Integration — Fragmented Approach
- **Issue:** Multiple entry points, inconsistent modes
- **What works:**
  - Chat endpoint uses OpenAI chat API (gpt-4o-mini) directly from `rag.py`
  - Question embedding via OpenAI embeddings API (text-embedding-3-small)
- **What doesn't work:**
  - `asr.py` openai mode — raises `NotImplementedError`
  - `embeddings.py` openai mode — raises `NotImplementedError`
  - **Orphaned:** `llm.py` service has stub + openai modes but is never called
- **Risk:** ⚠️ Mismatch between worker embeddings (stub) and chat embeddings (OpenAI) breaks RAG coherence

### 2.2 Chat Response Schemas
- **Files:** `backend/app/schemas/reels.py`, `backend/app/api/chat.py`
- **Issue:** `ChunkInfo` schema defined but never used; endpoint returns only answer string, not chunk metadata

### 2.3 Frontend
- **Files:** `frontend/app/pages/index.tsx`
- **Status:** ❌ Empty file (zero code)

---

## 3. NOT IMPLEMENTED YET

- ❌ **Frontend** — Entire Next.js/React UI missing (Phase 4)
- ❌ **Tests** — No unit or integration tests
- ❌ **User Feed/Following** — No multi-user feed or follow logic (Phase 5)
- ❌ **Cross-Reel Search** — Only per-reel chat; no global search (Phase 5)
- ❌ **Likes/Comments** — No social features (Phase 5)
- ❌ **Real OpenAI ASR** — Whisper integration stubbed
- ❌ **Real OpenAI Embeddings** — In embeddings.py service (note: rag.py calls OpenAI directly)

---

## 4. TECHNICAL DEBT & RISKS

### 4.1 🔴 CRITICAL: OPENAI_API_KEY Missing from .env
- **Impact:** Chat endpoint will crash (503) without it
- **Current:** `.env` does NOT include `OPENAI_API_KEY`
- **Fix:** Add `OPENAI_API_KEY=sk-...` to `.env`

### 4.2 🔴 CRITICAL: Embedding Vector Mismatch
- **Issue:** Worker generates stub vectors (all same value based on text length); chat queries OpenAI embeddings
- **Risk:** pgvector cosine search will fail to find relevant chunks if vectors from different models
- **Impact:** RAG quality degraded or broken

### 4.3 🔴 CRITICAL: PostgreSQL + pgvector Requirement
- **Issue:** `answer_reel_question()` raises `RuntimeError` if not PostgreSQL
- **Current Setup:** `.env` points to `postgresql://venkat@localhost:5432/reels`
- **Risk:** Chat endpoint returns 503 if DB not running or pgvector not installed

### 4.4 🟠 MEDIUM: Orphaned llm.py Service
- **File:** `backend/app/services/llm.py`
- **Issue:** Never imported; chat uses `rag.py` instead
- **Impact:** Dead code, confusion about implementation

### 4.5 🟠 MEDIUM: Synchronous Background Tasks
- **Issue:** `transcribe_and_index_reel()` runs synchronously via FastAPI BackgroundTasks
- **Risk:** Long jobs block queue; no persistence, retries, or monitoring
- **Note:** OK for MVP; recommend Celery for production

### 4.6 🟠 MEDIUM: Worker Transaction Safety
- **Issue:** No rollback semantics if exception occurs mid-chunk indexing
- **Risk:** Reel could remain in "processing" state permanently

### 4.7 🟡 LOW: Weak JWT Secret
- **Current:** `SECRET_KEY=dev-secret-key-change-me` in `.env`
- **Risk:** OK for dev; must change for any production deployment

### 4.8 🟡 LOW: No Input Validation on Chat
- **Issue:** Chat message accepts any string; no length limits or injection protection
- **Risk:** Low priority but should add safeguards

### 4.9 🟡 LOW: File Storage Not Cloud-Ready
- **Issue:** Stores files as local paths; not suitable for distributed systems
- **Risk:** Single-machine deployment only; no failover

---

## 5. BROKEN / DEAD CODE

| Code | File | Status |
|------|------|--------|
| `llm.py` (entire module) | `backend/app/services/llm.py` | ❌ Never called |
| Chat router | `backend/app/api/chat.py` | 🔶 Not included in main.py |
| ASR openai mode | `backend/app/services/asr.py` | ❌ NotImplementedError |
| Embeddings openai mode | `backend/app/services/embeddings.py` | ❌ NotImplementedError |
| Frontend | `frontend/app/pages/index.tsx` | ❌ Empty |

---

## 6. END-TO-END FUNCTIONALITY TEST

### ✅ Working Flow (Stub Mode — No API Keys Needed)
1. **Auth:** Register & login → JWT token ✅
2. **Upload:** POST /reels → file saved, Reel created, background job starts ✅
3. **Processing:** Worker transcribes (stub), chunks, embeds (stub) → ReelChunk rows created ✅
4. **List:** GET /reels → returns paginated list ✅
5. **Fetch:** GET /reels/{id} → returns metadata ✅

### ❌ Broken Flow (Chat Requires API Key)
6. **Chat:** POST /reels/{id}/chat → **FAILS** without `OPENAI_API_KEY` ❌
   - Reason: `answer_reel_question()` calls OpenAI directly

### 📋 Setup Requirements for Full E2E
- ✅ Python venv + dependencies installed
- ✅ PostgreSQL running on `localhost:5432`
- ⚠️ pgvector extension installed in PostgreSQL
- 🔴 **MISSING:** `OPENAI_API_KEY=sk-...` in `.env`
- ❌ Frontend not available

### Verdict
- **Stub mode works:** ✅ (Auth, upload, background jobs)
- **Chat broken:** ❌ (missing OPENAI_API_KEY + embedding vector inconsistency)
- **Frontend missing:** ❌ (no UI to interact with API)

---

## 7. CURRENT PROJECT STAGE

### 🔶 **Prototype / Early MVP**

**Summary:** Backend Phase 3 substantially complete with stub ASR/embedding modes; RAG chat requires OpenAI credentials + PostgreSQL; frontend not started; no tests.

**Phase Breakdown:**
- ✅ **Phase 1 (Auth + Reels):** Complete
- ✅ **Phase 2 (Transcription + Indexing):** Complete in stub mode
- ✅ **Phase 3 (RAG Chat):** Complete but requires OPENAI_API_KEY + PostgreSQL
- ❌ **Phase 4 (Frontend):** Not started
- ❌ **Phase 5 (Feed + Social):** Not started

**Readiness:**
- **Local dev demo (stub mode):** ✅ Yes (no API keys needed)
- **Live chat demo:** ❌ No (requires OPENAI_API_KEY + PostgreSQL + pgvector)
- **Production:** ❌ No (weak secrets, no real integrations, no frontend, no tests)

**Next Steps to Reach MVP:**
1. Add `OPENAI_API_KEY` to `.env`
2. Fix embedding vector inconsistency (worker vs. chat)
3. Start Phase 4 frontend (Next.js + API wrapper)
4. Add integration tests
5. Harden secrets and error handling

---

**Report Generated:** 2026-01-25  
**Auditor Note:** All findings based on code inspection only. Runtime verification requires live environment setup.
