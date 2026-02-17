# Frontend Integration Checklist

Verification list to ensure frontend works correctly with the backend.

## Prerequisites

- [ ] Backend running on `http://localhost:8000`
- [ ] Backend API returns `{status: "ok"}` on `GET /health`
- [ ] PostgreSQL database connected
- [ ] `.env.local` created with `NEXT_PUBLIC_API_URL`

## Setup Verification

- [ ] `npm install` completes without errors
- [ ] `npm run dev` starts without errors
- [ ] Page loads on `http://localhost:3000`
- [ ] No console errors (F12 → Console)

## Authentication Flow

### Registration
- [ ] Navigate to `/auth/register`
- [ ] Page displays correctly
- [ ] Can enter email, password, confirm
- [ ] Form validation works (email format, passwords match)
- [ ] Submit button sends POST to `/auth/register`
- [ ] Success: Token stored, redirected to `/reels`
- [ ] Error: Shows "Email already exists" if duplicate

### Login
- [ ] Navigate to `/auth/login`
- [ ] Form displays correctly
- [ ] Can enter email and password
- [ ] Submit button sends POST to `/auth/login`
- [ ] Success: Returns `{access_token, token_type}`
- [ ] Token stored in localStorage
- [ ] Redirected to `/reels` page
- [ ] Invalid creds return 401 (shows error)
- [ ] Invalid email/password shows "Invalid email or password"

### Protected Routes
- [ ] Direct access to `/reels` when logged out → redirects to login
- [ ] After login, `/auth/login` redirects to `/reels`
- [ ] Logging out clears token and redirects to login

## Video Upload Flow

- [ ] On `/reels`, see "Upload New Video" section
- [ ] Drag-and-drop zone displays
- [ ] Can drag video file → file shown in input
- [ ] Can click "Browse files" → file picker opens
- [ ] File validation works:
  - [ ] Only video formats accepted (MP4, MOV, AVI, MKV)
  - [ ] Files over 100MB rejected with error
- [ ] Title input accepts text
- [ ] Upload button sends POST to `/reels` (multipart form-data)
- [ ] Progress bar shows (0→100%)
- [ ] Success: Reel appears in list immediately
- [ ] Error: Shows error message below upload zone
- [ ] Reel has correct fields: id, title, status, created_at

## Reel List Page (`/reels`)

- [ ] Page displays correctly
- [ ] "My Reels" header visible
- [ ] "Sign Out" button in top right
- [ ] Upload zone section visible
- [ ] Reel grid displays (responsive)
- [ ] Each card shows:
  - [ ] Video thumbnail (or Play icon placeholder)
  - [ ] Title text
  - [ ] Status badge (uploading/processing/ready/failed)
  - [ ] Creation date
- [ ] Status badges have correct colors:
  - [ ] Yellow: uploading
  - [ ] Blue: processing
  - [ ] Green: ready
  - [ ] Red: failed
- [ ] Hover effect on cards (shadow/scale)
- [ ] Click card → navigates to `/reels/[id]`
- [ ] Empty state shows when no reels

## Reel Detail Page (`/reels/[id]`)

### Loading State
- [ ] Spinner shows while loading reel data
- [ ] GET `/reels/{id}` is called

### Video Player
- [ ] Video player displays
- [ ] Show video from `video_url` if status=ready
- [ ] Placeholder if still processing
- [ ] Play button works (pauses on play, resumes on pause)
- [ ] Mute button toggles sound
- [ ] Progress bar seekable
- [ ] Time display shows current/duration
- [ ] Fullscreen button works
- [ ] Responsive sizing

### Chat Interface
- [ ] Chat panel displays if video ready
- [ ] Shows "Chat will be available once processing is complete" if not ready
- [ ] Message input field with placeholder
- [ ] Send button
- [ ] Character counter shows count/2000
- [ ] Can type message and send
- [ ] POST `/reels/{id}/chat` is called with message
- [ ] Response appears as assistant message
- [ ] User message appears immediately
- [ ] Loading indicator shows while waiting
- [ ] Message history preserved during session
- [ ] Messages have timestamps
- [ ] Error shows if message exceeds 2000 chars

### Status Updates
- [ ] While video is processing, status updates every 2 seconds
- [ ] GET `/reels/{id}` is called repeatedly
- [ ] Status badge updates (uploading → processing → ready)
- [ ] Chat becomes enabled when status = ready
- [ ] Video player shows video when status = ready

## Error Handling

- [ ] Network error: Shows error message, not crash
- [ ] 401 unauthorized: Auto-logout, redirect to login
- [ ] 404 not found: Shows "Reel not found" message
- [ ] 500 server error: Shows error detail from backend
- [ ] Invalid input: Form validation prevents submit
- [ ] File upload error: Shows error message below zone

## State Persistence

- [ ] Refresh page → user stays logged in (token in localStorage)
- [ ] Refresh `/reels/[id]` → reel data reloaded correctly
- [ ] Logout → token cleared from localStorage
- [ ] Session storage works (message history during session)

## UI/UX Details

- [ ] All buttons have hover states
- [ ] Loading spinners appear for async operations
- [ ] Form validation errors show inline
- [ ] Success messages display appropriately
- [ ] Empty states show helpful messages
- [ ] Mobile view is responsive (test on devtools)
- [ ] No console warnings/errors
- [ ] Keyboard navigation works (Tab, Enter)

## Performance

- [ ] Initial load time < 3 seconds
- [ ] Reel list loads < 1 second (cached)
- [ ] Chat response < 5 seconds (backend dependent)
- [ ] No unnecessary API calls
- [ ] No memory leaks (check DevTools Memory)

## Backend Integration

- [ ] All API endpoints are called correctly
- [ ] Request headers include Authorization token
- [ ] Response data is displayed correctly
- [ ] Error responses are handled gracefully
- [ ] Content-Type headers are correct (JSON, multipart)

## Sign Out Flow

- [ ] Click "Sign Out" button
- [ ] Token cleared from localStorage
- [ ] Redirected to `/auth/login`
- [ ] Cannot access `/reels` without re-login

## Cross-Browser Testing

- [ ] Chrome: ✅/❌
- [ ] Firefox: ✅/❌
- [ ] Safari: ✅/❌
- [ ] Edge: ✅/❌
- [ ] Mobile Safari: ✅/❌
- [ ] Chrome Mobile: ✅/❌

## Final Verification

- [ ] All core flows work (auth, upload, browse, chat)
- [ ] No errors in browser console
- [ ] No TypeScript errors (`npm run type-check`)
- [ ] No linting errors (`npm run lint`)
- [ ] Performance is acceptable
- [ ] UI looks polished
- [ ] Mobile responsive
- [ ] Ready for deployment

---

## Quick Test Script

```bash
# Start backend
cd ../backend
python -m uvicorn app.main:app --reload

# In another terminal, start frontend
cd ../frontend
npm run dev

# Open http://localhost:3000

# Test Registration
# 1. Go to http://localhost:3000/auth/register
# 2. Enter: test@example.com / Password123
# 3. Should redirect to /reels

# Test Upload
# 1. Drag a video file to the upload zone
# 2. Enter title "Test Video"
# 3. Click Upload
# 4. Should appear in list with "uploading" status

# Test Chat
# 1. Wait for video to finish processing (status = ready)
# 2. Click on the video
# 3. In chat panel, type "What's in this video?"
# 4. Should get AI response

# Test Logout
# 1. Click "Sign Out" button
# 2. Should redirect to login page
```

---

## Troubleshooting Reference

### Frontend won't start
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Backend connection fails
```bash
# Check backend is running
curl http://localhost:8000/health
# Should see: {"status": "ok", "database": "connected"}
```

### Chat not working
```bash
# Check video status is "ready"
curl http://localhost:8000/reels/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
# Should show status: "ready"
```

### Token not persisting
```bash
# Check localStorage in DevTools (F12 → Application → Storage)
# Should see "auth_token" key with JWT value
```

---

## Sign-Off

**Frontend Status**: Ready for Testing ✅
**Backend Integration**: Complete ✅
**Documentation**: Comprehensive ✅

Date Completed: [TODAY]
