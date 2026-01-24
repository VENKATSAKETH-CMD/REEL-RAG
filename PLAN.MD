0. Tech stack (don’t overthink this)
Pick something Copilot is very good at:
Backend
Python + FastAPI
PostgreSQL (+ pgvector for embeddings)
SQLAlchemy or SQLModel
Background jobs: Celery or a simple in-process task queue to start
AI
ASR: Whisper API (or any speech-to-text API)
LLM: OpenAI GPT-4 / GPT-4.1 / whatever you have
Embeddings: OpenAI embeddings stored in pgvector
Frontend
Next.js + TypeScript (standard, Copilot is strong here)
If you don’t like Next.js, fine, use plain React + Vite, but don’t change everything at once.
1. Repo structure (put this in PLAN.md)
instagram-reel-ai/
  backend/
    app/
      main.py
      api/
        reels.py        # upload/list/get reels
        chat.py         # per-reel chat
      models/
        user.py
        reel.py
        transcript.py
      db/
        session.py
        base.py
      services/
        storage.py      # S3 or local file saving
        asr.py          # Whisper calls
        embeddings.py   # embedding calls
        rag.py          # retrieval + prompt building
      workers/
        tasks.py        # background transcription/index tasks
    tests/
  frontend/
    app/ or src/
      pages/
      components/
        ReelCard.tsx
        ReelPlayer.tsx
        ReelChat.tsx
      lib/
        api.ts          # axios/fetch wrappers
  PLAN.md
  README.md
Create this structure first (empty files are fine). Copilot works better when the skeleton exists.
2. Phase 1 – Minimal backend: users + reels
Goal
Sign up / login
Upload reel (store file path & metadata)
List reels
What to put in PLAN.md for this phase
Phase 1 – Minimal backend (auth + reels)
- Implement SQLModel models: User, Reel
- Setup Postgres connection and create tables
- Auth: simple JWT-based login/register
- Reels API:
  - POST /reels: upload video file, save to storage, create Reel row
  - GET /reels: list recent reels (no feed logic yet)
  - GET /reels/{id}: get reel metadata
- No AI yet, just storage.
How to “talk” to Copilot in code
In backend/app/models/reel.py:
# TODO: Define SQLModel for Reel with:
# - id (int, primary key)
# - user_id (foreign key to User)
# - video_url (str)
# - title (str, optional)
# - created_at (datetime)
# - status (enum: "uploaded", "processing", "ready", "failed")
#
# Use SQLModel with __tablename__ = "reels".
Let Copilot fill it, then you check and fix.
In backend/app/api/reels.py:
# TODO: Implement FastAPI router for reels:
# - POST /reels: accept multipart form with file + title.
#   Save file using services.storage, create Reel row, return reel.
# - GET /reels: return paginated list of reels ordered by created_at desc.
# - GET /reels/{reel_id}: return single reel.
#
# Assume user is already authenticated (we'll plug auth later).
This kind of precise TODO is how you “communicate the plan” to Copilot.
3. Phase 2 – ASR + transcription + indexing
Goal
When a reel is uploaded:
Run ASR → transcript
Chunk + embed transcript
Store in DB (for RAG)
Add this to PLAN.md:
Phase 2 – Transcription + RAG indexing
- Add tables:
  - ReelTranscript: reel_id, full_text
  - ReelChunk: reel_id, chunk_index, text, embedding (vector)
- After POST /reels:
  - Enqueue background job: transcribe_and_index_reel(reel_id)
- Implement services:
  - asr.py: call Whisper API with video file, return transcript text
  - embeddings.py: call OpenAI embeddings
  - rag.py: chunk text, embed, store ReelChunk rows
- Update Reel.status as it moves: "uploaded" -> "processing" -> "ready"
In backend/app/workers/tasks.py:
# TODO: Implement function transcribe_and_index_reel(reel_id: int):
# 1. Load Reel from DB, get video_url.
# 2. Download file path or open from storage.
# 3. Call services.asr.transcribe_video(...) to get transcript text.
# 4. Save ReelTranscript row.
# 5. Chunk transcript text into ~300-token chunks with overlap.
# 6. For each chunk, call services.embeddings.embed_text(...) and save ReelChunk rows.
# 7. Set Reel.status = "ready" if everything succeeds, or "failed" on error.
In backend/app/services/rag.py:
# TODO: Implement:
# - chunk_text(text: str) -> list[str]
# - get_chunks_for_reel(reel_id: int) -> List[ReelChunk]
# - retrieve_chunks_for_question(reel_id: int, question: str, top_k: int = 5)
#
# Use pgvector cosine similarity in SQL to retrieve top_k chunks filtered by reel_id.
You’re explicitly telling Copilot: we are doing RAG, scoped by reel_id.
4. Phase 3 – Per-reel chat endpoint (the core RAG bot)
Goal
Endpoint: POST /reels/{id}/chat
Input: { "question": "..." }
Output: { "answer": "...", "chunks_used": [...] }
Add to PLAN.md:
Phase 3 – Per-reel RAG chat
- Implement POST /reels/{id}/chat:
  - Validate reel exists and status == "ready".
  - Use rag.retrieve_chunks_for_question(reel_id, question).
  - Build prompt with:
    - System: "You explain only this video. Use only the transcript context."
    - Context: top chunks' texts
    - User: question
  - Call OpenAI chat completion, return answer + snippet of used chunks.
- No global search yet, only per-reel chat.
In backend/app/api/chat.py:
# TODO: Implement POST /reels/{reel_id}/chat endpoint:
# Request body: {"question": "string"}
# Steps:
# - Load reel, ensure status == "ready"
# - Use rag.retrieve_chunks_for_question(reel_id, question, top_k=5)
# - Build system + user messages:
#   System: explain ONLY this reel using provided transcript. Do not invent steps.
# - Call OpenAI chat completion and return JSON:
#   {"answer": "...", "chunks": [{"id": ..., "text": "..."}]}
Again, you’re giving Copilot all design decisions up front.
5. Phase 4 – Frontend: basic UI + per-reel explainer
Goal
Show list of reels
Reel detail page with:
Video player
“AI summary”
Chat box for questions
Add to PLAN.md:
Phase 4 – Frontend integration
- Pages:
  - /reels: list all reels
  - /reels/[id]: reel detail
- Components:
  - ReelCard: thumbnail, title, created_at
  - ReelPlayer: html5 video + status badges
  - ReelChat:
    - shows AI summary (first call to /reels/{id}/chat with "Summarize this reel")
    - input box for user questions
    - list of Q&A pairs
- API wrapper in frontend/lib/api.ts:
  - getReels(), getReel(id), chatWithReel(id, question)
In frontend/components/ReelChat.tsx:
// TODO: Implement ReelChat component:
//
// Props: { reelId: number }
// State:
//   - messages: { role: "user" | "assistant"; text: string }[]
//   - loading: boolean
//
// Behavior:
//   - On mount, call chatWithReel(reelId, "Give a short summary of this reel.")
//     and add assistant message.
//   - When user submits a question:
//     - Append user message
//     - Call chatWithReel(reelId, question)
//     - Append assistant answer
This is exactly the kind of comment Copilot loves.
6. Phase 5 – Extras (later, not now)
If you survive the above and it works:
Add likes / comments.
Add simple following + “My following” feed.
Add cross-reel search (different endpoint, different RAG scope).
Add auth, JWT, etc. after you have the vertical slice working.
Don’t start here. You’ll never finish.
7. How to keep Copilot aligned
Keep PLAN.md at the root and update it as you go.
Copilot reads open files and nearby context.
Start each new file with a short comment block saying what this file is for and what functions you expect.
Make TODOs very specific, like I showed.
“Do auth” is useless.
“Implement login endpoint: POST /auth/login, accepts email/password, returns JWT” is good.
Review every Copilot suggestion.
If it goes off-plan, reject it and tighten your TODO comment.