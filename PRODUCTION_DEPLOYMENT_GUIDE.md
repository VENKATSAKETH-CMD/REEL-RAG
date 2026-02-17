# 🚀 PRODUCTION DEPLOYMENT GUIDE

**Status:** Ready for 24-hour production launch  
**Last Updated:** Feb 10, 2026  
**Components:** FastAPI Backend + Next.js Frontend

---

## PRE-DEPLOYMENT CHECKLIST

### 1. ✅ Environment Variables
```bash
# Backend: Create .env in root of /backend
cd backend
cp .env.production .env
# Edit .env with production values:
# - DATABASE_URL (PostgreSQL connection string)
# - SECRET_KEY (generated secret)
# - ALLOWED_ORIGINS (your production domains)
# - OPENAI_API_KEY (if using real chat)
```

### 2. ✅ Frontend Configuration
```bash
# Frontend: Create .env.local
cd frontend
echo "NEXT_PUBLIC_API_BASE_URL=https://api.yourdomain.com" > .env.local
```

### 3. ✅ Database Setup
```bash
# PostgreSQL must be running on production server
# Run migrations (none needed currently, SQLModel auto-creates)
# Verify pgvector extension installed:
psql postgresql://user:password@host:5432/reel_rag_prod
> CREATE EXTENSION IF NOT EXISTS vector;
> \q
```

---

## DEPLOYMENT OPTIONS

### Option A: Heroku (Easiest for MVP)

#### Step 1: Set up Heroku apps
```bash
# Create backend app
heroku create reel-rag-api
heroku addons:create heroku-postgresql:standard-0 -a reel-rag-api

# Create frontend app  
heroku create reel-rag-web
```

#### Step 2: Set environment variables
```bash
# Backend config
heroku config:set -a reel-rag-api \
  SECRET_KEY="your-secret-key" \
  ALLOWED_ORIGINS="https://reel-rag-web.herokuapp.com" \
  ENVIRONMENT="production"

# Backend: Add DATABASE_URL automatically set by Heroku addon

# Frontend config
heroku config:set -a reel-rag-web \
  NEXT_PUBLIC_API_BASE_URL="https://reel-rag-api.herokuapp.com"
```

#### Step 3: Deploy backend
```bash
# From project root
git subtree push --prefix backend heroku-backend main
# Or: cd backend && git push heroku main
```

#### Step 4: Deploy frontend
```bash
# From project root
git subtree push --prefix frontend heroku-frontend main
# Or: cd frontend && git push heroku main
```

#### Step 5: Verify
```bash
heroku logs -a reel-rag-api --tail
curl https://reel-rag-api.herokuapp.com/health
# Should see: {"status":"ok","database":"ok"}
```

---

### Option B: AWS (More Control)

#### Backend: EC2 + RDS
```bash
# 1. Launch EC2 (Ubuntu 22.04)
# 2. Install dependencies
ssh -i key.pem ubuntu@instance-ip
sudo apt update && sudo apt install -y python3.10 python3-pip postgresql-client
cd /home/ubuntu
git clone your-repo
cd your-repo/backend

# 3. Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Create .env
echo "DATABASE_URL=postgresql://user:pass@rds-endpoint:5432/reel_rag" > .env
echo "SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')" >> .env
echo "ALLOWED_ORIGINS=https://yourdomain.com" >> .env

# 5. Run with Gunicorn (production ASGI server)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app.main:app

# 6. Use systemd service for auto-restart (see systemd config below)
```

#### Frontend: S3 + CloudFront
```bash
# 1. Build for production
cd frontend
npm run build

# 2. Deploy to S3
aws s3 sync out/ s3://your-frontend-bucket/ --delete

# 3. Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id YOUR_ID --paths "/*"
```

---

### Option C: DigitalOcean (Best Value)

#### Deploy with Docker
```bash
# Create Dockerfile for backend
# See Dockerfile section below

# Push to DigitalOcean Container Registry
docker build -t backend:latest ./backend
doctl registry login
docker tag backend:latest registry.digitalocean.com/your-registry/backend:latest
docker push registry.digitalocean.com/your-registry/backend:latest

# Deploy via DigitalOcean App Platform
# Configure via web console pointing to your registry
```

---

## DOCKER DEPLOYMENT (Any Platform)

### Backend Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/app ./app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with Gunicorn (production server)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "--timeout", "120", "app.main:app"]
```

### Frontend Dockerfile
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend .
RUN npm run build

FROM node:18-alpine

WORKDIR /app

COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/package.json ./

EXPOSE 3000

CMD ["npm", "start"]
```

### docker-compose.yml
```yaml
version: '3.9'

services:
  postgres:
    image: pgvector/pgvector:pg15
    environment:
      POSTGRES_USER: reel_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: reel_rag
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://reel_user:${DB_PASSWORD}@postgres:5432/reel_rag
      SECRET_KEY: ${SECRET_KEY}
      ALLOWED_ORIGINS: http://frontend:3000,https://yourdomain.com
      ENVIRONMENT: production
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build: ./frontend
    environment:
      NEXT_PUBLIC_API_BASE_URL: http://backend:8000
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
```

---

## SYSTEMD SERVICE (Linux)

Create `/etc/systemd/system/reel-rag-backend.service`:

```ini
[Unit]
Description=Reel RAG Backend
After=network.target

[Service]
Type=notify
User=ubuntu
WorkingDirectory=/home/ubuntu/reel-rag/backend
ExecStart=/home/ubuntu/reel-rag/backend/venv/bin/gunicorn \
    -w 4 \
    -b 0.0.0.0:8000 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    app.main:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable reel-rag-backend
sudo systemctl start reel-rag-backend
sudo systemctl status reel-rag-backend
```

---

## POST-DEPLOYMENT VALIDATION

### 1. Health Checks
```bash
# Backend health
curl -s https://api.yourdomain.com/health | jq .
# Expected: {"status":"ok","database":"ok"}

# Frontend health
curl -s https://yourdomain.com | grep -i "Reel RAG"
# Should return HTML with app title
```

### 2. End-to-End Test Flow
```bash
# 1. Open https://yourdomain.com in browser
# 2. Register: test@prod.com / Test123!
# 3. Upload a video file
# 4. Wait for status = "ready"
# 5. Send chat message
# 6. Verify AI response received

# All with NO browser console errors
```

### 3. Monitor Logs
```bash
# Heroku
heroku logs --tail

# DigitalOcean App Platform
doctl apps logs <app-id>

# Linux/systemd
journalctl -u reel-rag-backend -f

# Docker
docker logs -f container_name
```

### 4. Performance Baseline
```
Expected:
- Registration: < 1 second
- Login: < 1 second  
- Video upload: 10-30 seconds (depends on size)
- Chat response: 3-5 seconds (with OpenAI)
- Page load: < 2 seconds
- No CORS errors in console
- HTTPS working (no mixed content warnings)
```

---

## CRITICAL: HTTPS/SSL

**Must have HTTPS in production!**

### Option 1: Let's Encrypt (Free)
```bash
# Using Certbot
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly -d api.yourdomain.com -d yourdomain.com
sudo certbot renew --dry-run  # Test auto-renewal

# Configure nginx/haproxy to use certificates
```

### Option 2: AWS Certificate Manager (Free with AWS)
- Request certificate in AWS Console
- Verify domain ownership via DNS
- Attach to ALB/CloudFront

### Option 3: Heroku/Vercel (Built-in)
- Automatic HTTPS included
- Free Let's Encrypt renewal

---

## ROLLBACK PLAN

If deployment fails:

```bash
# Heroku
git revert HEAD
git push heroku main

# Docker
docker rollback service-name previous-version

# Manual
# Keep previous working tag in git
git checkout v0.1.0-prod
./deploy.sh
```

---

## MONITORING & ALERTS

### Recommended Tools
- **Errors**: Sentry, Rollbar
- **Performance**: DataDog, New Relic
- **Logs**: CloudWatch, ELK Stack
- **Uptime**: StatusPage, Pingdom

### Setup Sentry (Recommended)
```python
# backend/app/main.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN", None),
    integrations=[FastApiIntegration()],
    environment=os.getenv("ENVIRONMENT", "development"),
)
```

---

## 24-HOUR TIMELINE

| Time | Task | Duration |
|------|------|----------|
| Hour 0-1 | ✅ Environment setup, .env files | 1h |
| Hour 1-2 | ✅ Local testing (register→upload→chat) | 1h |
| Hour 2-4 | ✅ Choose platform, create accounts | 2h |
| Hour 4-8 | ✅ Deploy backend + database | 4h |
| Hour 8-12 | ✅ Deploy frontend | 4h |
| Hour 12-20 | ✅ Production testing & fixes | 8h |
| Hour 20-24 | ✅ Buffer for issues + documentation | 4h |

---

## SUPPORT

If issues occur during deployment:

1. **Check logs first** (most issues obvious in logs)
2. **Verify environment variables** set correctly
3. **Test database connection** independently
4. **Check CORS configuration** matches domain
5. **Verify SECRET_KEY is strong** (32+ chars)

---

**YOU'RE READY. Let's deploy!** 🚀
