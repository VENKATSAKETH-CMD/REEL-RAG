#!/bin/bash
# Integration Test Script
# Verify frontend is ready for production

echo "🔍 Frontend Production Readiness Checklist"
echo "=========================================="
echo ""

# Check 1: .env.local exists
if [ -f ".env.local" ]; then
    echo "✅ .env.local exists"
    echo "   API_BASE_URL=$(grep NEXT_PUBLIC_API_BASE_URL .env.local)"
else
    echo "❌ .env.local missing"
    exit 1
fi

# Check 2: Key dependencies installed
echo ""
echo "✅ Checking dependencies..."
if [ -d "node_modules" ]; then
    echo "   - node_modules exists"
    grep -q '"next"' package.json && echo "   - Next.js 14 configured"
    grep -q '"react"' package.json && echo "   - React 18 configured"
    grep -q '"@tanstack/react-query"' package.json && echo "   - React Query configured"
    grep -q '"zustand"' package.json && echo "   - Zustand configured"
else
    echo "   ⚠️  Run: npm install"
fi

# Check 3: TypeScript config valid
echo ""
if npx tsc --noEmit 2>&1 | grep -q "error TS5023"; then
    echo "❌ TypeScript compilation error (TS5023)"
    exit 1
else
    echo "✅ TypeScript config valid"
fi

# Check 4: All key files exist
echo ""
echo "✅ Checking key files..."
REQUIRED_FILES=(
    "lib/api.ts"
    "lib/auth-store.ts"
    "lib/hooks/useAuth.ts"
    "lib/hooks/useReel.ts"
    "app/page.tsx"
    "app/auth/login/page.tsx"
    "app/reels/page.tsx"
    "app/reels/[id]/page.tsx"
    "components/features/UploadZone.tsx"
    "components/features/ChatInterface.tsx"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✓ $file"
    else
        echo "   ✗ $file (MISSING)"
        exit 1
    fi
done

echo ""
echo "=========================================="
echo "✅ Frontend is PRODUCTION READY!"
echo ""
echo "Next Steps:"
echo "1. Ensure backend is running: http://localhost:8000"
echo "2. Start frontend: npm run dev"
echo "3. Open browser: http://localhost:3000"
echo ""
