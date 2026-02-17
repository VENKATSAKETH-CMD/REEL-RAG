# QUICK START - Run the MVP in 10 Minutes

## Prerequisites
- Python 3.9+
- PostgreSQL with pgvector installed
- pip

## Step 1: Setup Database (2 min)

```bash
# Create PostgreSQL database
createdb reel_rag_dev

# Enable pgvector
psql reel_rag_dev -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

## Step 2: Setup Backend (3 min)

```bash
cd backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Edit .env and set DATABASE_URL
# DATABASE_URL=postgresql://postgres:password@localhost:5432/reel_rag_dev
```

## Step 3: Start Backend (1 min)

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
✅ Startup complete - server is ready
```

## Step 4: Test (4 min)

**Option A: Automated Test**
```bash
# In another terminal:
cd backend
python test_integration.py
```

**Option B: Manual Test**
```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'

# Login
curl -X POST http://localhost:8000/auth/login \
  -d "username=user@example.com" \
  -d "password=password123"
# Save the access_token as TOKEN

# Create test video
dd if=/dev/zero of=test.mp4 bs=1M count=1

# Upload
curl -X POST http://localhost:8000/reels \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test.mp4" \
  -F "title=Test Video"
# Save the reel_id

# Wait 3 seconds
sleep 3

# Check status (should be "ready")
curl -X GET http://localhost:8000/reels/1 \
  -H "Authorization: Bearer $TOKEN"

# Chat
curl -X POST http://localhost:8000/reels/1/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What was discussed?"
  }'
```

**Option C: Swagger UI**
- Open http://localhost:8000/docs
- Click "Authorize" and login
- Try endpoints interactively

---

## What You're Testing

✅ **Reel Upload**: Video file saved to disk  
✅ **Background Processing**: Transcription + chunking + embedding  
✅ **Status Tracking**: uploaded → processing → ready  
✅ **RAG Search**: Embedding consistency between indexing and retrieval  
✅ **Chat**: Question answering based on transcript  
✅ **Error Handling**: Safe fallbacks if something fails  

---

## Success Indicators

- [ ] Server starts without errors (✅ Startup complete)
- [ ] Health check returns {"status": "ok"}
- [ ] Can register and login
- [ ] Video uploads successfully
- [ ] Status changes from "uploaded" to "processing" to "ready"
- [ ] Chat endpoint returns an answer
- [ ] No HTTP 500 errors
- [ ] Reel never stuck in "processing"

---

## For Production

See `SETUP.md` for:
- Full architecture overview
- Performance tuning
- Deployment options
- Troubleshooting guide

---

**That's it! The MVP is now testable end-to-end. 🚀**
