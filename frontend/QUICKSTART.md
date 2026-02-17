# Frontend Quick Start

Get the frontend running in 5 minutes.

## Prerequisites

- Node.js 18+ installed
- Backend running on `http://localhost:8000`
- (Optional) GitHub Desktop or Git CLI

## Installation

### 1. Navigate to frontend directory
```bash
cd frontend
```

### 2. Install dependencies
```bash
npm install
```

This installs Next.js, React, TypeScript, Tailwind, and all required packages (~500MB).

### 3. Create environment file
```bash
cp .env.example .env.local
```

Edit `.env.local` if your backend is on a different URL:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Running

### Development mode
```bash
npm run dev
```

Open http://localhost:3000 in your browser.

You should see the login page. If backend is running, you can register a new account.

### Production build
```bash
npm run build
npm start
```

## Troubleshooting

### Port 3000 already in use?
```bash
npm run dev -- -p 3001
```

### Backend connection failing?
```bash
# Check backend is running
curl http://localhost:8000/health

# Should see: {"status": "ok", "database": "connected"}
```

If not, start backend:
```bash
cd ../backend
python -m uvicorn app.main:app --reload
```

### Slow installation?
```bash
# Use yarn if available (faster)
yarn install
yarn dev

# Or pnpm (fastest)
pnpm install
pnpm dev
```

## What Works

- ✅ Login / Register
- ✅ Video upload with drag-and-drop
- ✅ Video list with status badges
- ✅ Video player with controls
- ✅ AI chat about videos (when processing complete)
- ✅ Real-time status updates

## Next Steps

1. **Test Registration**: Create account at `/auth/register`
2. **Upload Video**: Drag-and-drop a video on the reels page
3. **Wait for Processing**: Status changes from "uploading" → "processing" → "ready"
4. **Try Chat**: Click video → ask questions in the chat panel

## Architecture Overview

```
Frontend (Next.js)
├── Auth Pages (login, register)
├── Reel Management (upload, list, detail)
└── Chat Interface (video + AI chat)
       ↓ (API calls)
    Backend (FastAPI)
    ├── Auth (JWT)
    ├── Video Storage (S3/local)
    ├── Processing (async)
    └── RAG + LLM (OpenAI/local)
```

## File Structure

```
frontend/
├── app/              # Pages and layouts
│   ├── auth/
│   ├── reels/
│   └── layout.tsx    # Root layout with providers
├── components/       # Reusable components
│   ├── ui/          # Design system
│   └── features/    # Feature components
├── lib/             # Utilities and state
│   ├── api.ts       # API client
│   ├── hooks/       # Custom hooks
│   └── *-store.ts   # Zustand stores
└── styles/          # Global styles
```

## Key Features

### 1. Authentication
- JWT token stored in localStorage
- Protected routes (redirect to login)
- Auto-logout on 401 response

### 2. Upload
- Drag-and-drop or click to select
- File validation (video types, 100MB max)
- Progress indicator
- Error messages

### 3. Processing Status
- Real-time status updates (polling every 2s)
- Status badges: uploading, processing, ready, failed
- Chat only available when ready

### 4. Video Chat
- Play video while chatting
- AI responds to questions about video
- Message history in conversation
- 2000 char limit with live counter

## Common Commands

```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Type check
npm run type-check

# Lint
npm run lint
```

## API Contracts

Frontend communicates with backend via REST API:

```
POST   /auth/register          → { access_token, token_type }
POST   /auth/login             → { access_token, token_type }
POST   /reels                  → { id, status, ... }
GET    /reels                  → { reels: [...] }
GET    /reels/{id}             → { id, status, ... }
POST   /reels/{id}/chat        → { answer: "..." }
GET    /health                 → { status, database }
```

## Performance Tips

1. **First Load**: ~2-3s (Next.js + React hydration)
2. **Video Upload**: Depends on file size (shows progress)
3. **Processing**: 30s-5min (backend dependent)
4. **Chat Response**: 2-10s (LLM response time)

## Deployment

### Vercel (Recommended)
```bash
npm i -g vercel
vercel
```

### Docker
```bash
docker build -t reel-rag-frontend .
docker run -p 3000:3000 reel-rag-frontend
```

### Manual (VPS, AWS, etc.)
```bash
npm run build
npm start
# Or use PM2: pm2 start npm -- start
```

## Support

- Check browser console (F12) for errors
- Check backend logs for API issues
- Verify environment variables are loaded
- Clear browser cache/cookies if issues persist

## Next Phase

Once running smoothly, consider:
- [ ] Add video thumbnails
- [ ] Implement pagination for reel list
- [ ] Add reel deletion/editing
- [ ] Implement search/filter
- [ ] Add user profile page
- [ ] Add analytics/tracking
