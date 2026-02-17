# Reel RAG Frontend

Premium Next.js frontend for video intelligence platform with AI-powered Q&A.

## Stack

- **Framework**: Next.js 14 (App Router) with TypeScript
- **Styling**: Tailwind CSS with custom design system
- **UI Components**: Radix UI + custom components
- **State Management**: Zustand (auth) + TanStack Query (data)
- **Animations**: Framer Motion
- **HTTP Client**: Axios
- **Icons**: Lucide React

## Project Structure

```
frontend/
├── app/
│   ├── auth/
│   │   ├── login/page.tsx          # Login page
│   │   ├── register/page.tsx       # Registration page
│   │   └── layout.tsx              # Auth layout
│   ├── reels/
│   │   ├── page.tsx                # Reel list (main hub)
│   │   ├── [id]/page.tsx           # Reel detail with video + chat
│   │   └── layout.tsx              # Protected layout
│   ├── layout.tsx                  # Root layout with providers
│   └── globals.css                 # Global styles
├── components/
│   ├── ui/                         # Design system
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Card.tsx
│   │   └── ...
│   └── features/                   # Feature components
│       ├── UploadZone.tsx          # Drag-and-drop upload
│       ├── ReelCard.tsx            # Reel preview
│       ├── VideoPlayer.tsx         # Video with controls
│       ├── ChatInterface.tsx       # AI chat
│       └── ChatMessage.tsx         # Message bubble
├── lib/
│   ├── api.ts                      # Axios API client
│   ├── auth-store.ts               # Auth state (Zustand)
│   ├── reel-store.ts               # Reel state (Zustand)
│   ├── utils.ts                    # Utilities (cn, etc.)
│   └── hooks/
│       ├── useAuth.ts              # Auth hooks
│       └── useReel.ts              # Reel data hooks
├── middleware.ts                   # Route protection
├── package.json
├── tsconfig.json
├── next.config.js
├── tailwind.config.ts
├── postcss.config.js
└── README.md
```

## Getting Started

### Prerequisites

- Node.js 18+
- npm/yarn/pnpm
- Backend running at `http://localhost:8000`

### Installation

```bash
cd frontend
npm install
```

### Environment Setup

Create `.env.local`:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Development

```bash
npm run dev
```

Open http://localhost:3000

### Build

```bash
npm run build
npm start
```

## Features

### 1. Authentication
- Email/password registration
- JWT-based login
- Token storage in localStorage
- Protected routes with middleware
- Auto-redirect to login if unauthorized

### 2. Video Upload
- Drag-and-drop zone
- File validation (MP4, MOV, etc. | max 100MB)
- Progress tracking
- Title input
- Graceful error handling

### 3. Reel Management
- List all uploaded videos
- Status badges (uploading, processing, ready, failed)
- Grid view with hover effects
- Timestamps and metadata

### 4. Video Playback
- HTML5 video player
- Play/pause, mute, fullscreen controls
- Progress bar with seek
- Time display
- Responsive sizing

### 5. AI Chat
- Message history
- Real-time responses from backend
- 2000 character limit with validation
- User/assistant message styling
- Auto-scroll to latest message
- Thinking state indicator
- Error handling with retry

### 6. Polish
- Smooth animations (Framer Motion)
- Loading states (skeletons, spinners)
- Error boundaries
- Empty states
- Focus management
- Keyboard support (Tab, Enter, Escape)

## API Integration

### Auth Endpoints

```typescript
POST /auth/register
POST /auth/login          → { access_token, token_type }
```

### Reel Endpoints

```typescript
POST /reels               → { id, status, video_url, ... }
GET /reels                → { reels: Reel[] }
GET /reels/{id}           → { id, status, video_url, ... }
POST /reels/{id}/chat     → { message } → { answer }
```

## State Management

### Auth Store (Zustand)
- `user`: Current user object
- `token`: JWT token
- `setUser()`, `setToken()`, `logout()`

### Reel Store (Zustand)
- `reels`: List of reels
- `currentReel`: Selected reel
- `uploadProgress`: Progress percentage
- `updateReel()`, `setCurrentReel()`, etc.

### React Query
- Handles all server state (reels list, reel detail, chat)
- Auto caching, refetching, error handling
- Configured with 5min staleTime, 10min gcTime

## Styling

### Design System

**Colors**:
- Primary: Cyan 500 (interactive)
- Secondary: Slate (text, borders, bg)
- Success: Green 600
- Warning: Yellow 600
- Error: Red 600

**Components**:
- Button (4 variants: primary, secondary, outline, ghost)
- Input (with error state)
- Card (container with hover option)
- Spinner (loading indicator)
- ChatMessage (bubble styling)

**Animations**:
- pulse-soft: Gentle pulsing effect (3s)
- shimmer: Loading skeleton shimmer (2s)
- smooth-transition: Used throughout for hover/focus effects

## Development Workflow

1. **Component Development**: Add UI in `components/ui/` or `components/features/`
2. **Page Creation**: Add routes in `app/`
3. **Data Fetching**: Use hooks from `lib/hooks/`
4. **State Management**: Use Zustand stores or React Query
5. **Styling**: Use Tailwind classes + custom components

## Best Practices

- Use `'use client'` directive for client-side logic
- Keep components small and focused
- Use TypeScript for type safety
- Wrap async operations with try-catch
- Validate user input before sending to API
- Show loading states during async operations
- Provide clear error messages
- Test on mobile (responsive)

## Troubleshooting

### Backend connection failing?
- Verify backend is running on http://localhost:8000
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Look at browser console for network errors

### Auth not persisting?
- Check browser localStorage is enabled
- Verify token is saved after login
- Clear cookies/localStorage and try again

### Video not loading?
- Ensure backend serves video with correct CORS headers
- Check video_url is valid and accessible
- Verify video format is supported (MP4 is most compatible)

### Chat not responding?
- Confirm backend is running and processing videos
- Check video status is "ready" before chatting
- Verify message is under 2000 characters
- Check browser console for API errors

## Production Deployment

### Build
```bash
npm run build
```

### Environment
Create `.env.production.local`:
```bash
NEXT_PUBLIC_API_URL=https://your-backend-url.com
```

### Deploy to Vercel
```bash
vercel deploy
```

Or any Node.js hosting (AWS, DigitalOcean, Heroku, etc.)

## Performance Optimization

- Image optimization (next/image)
- Code splitting via dynamic imports
- Lazy loading components with React.lazy
- Optimized CSS with Tailwind purging
- Caching strategy via React Query

## License

MIT
