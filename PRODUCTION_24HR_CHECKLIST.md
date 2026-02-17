# 🚀 24-Hour Production Deployment Checklist

**Deadline:** 24 hours from now (Feb 11, 2026)  
**Status:** IN PROGRESS  
**Current Time:** Feb 10, 2026

---

## ⚠️ CRITICAL BLOCKERS (Must Fix First)

### 1. **CORS Configuration** 
- [ ] CORS hardcoded to localhost only
- [ ] Need environment variable: `ALLOWED_ORIGINS`
- [ ] File: `/backend/app/main.py` line 148-155
- **Action:** Make CORS dynamic based on environment

### 2. **SECRET_KEY**
- [ ] Default value in code: `"dev-secret-key-change-me"`
- [ ] File: `/backend/app/db/session.py`
- **Action:** Generate strong production key, store in `.env`

### 3. **Database Configuration**
- [ ] Currently supports PostgreSQL (good!)
- [ ] Need production `DATABASE_URL` set
- **Action:** Provide connection string

### 4. **Frontend API URL**
- [ ] Uses `NEXT_PUBLIC_API_BASE_URL` env var (good!)
- [ ] Need production API domain set
- **Action:** Set before build

### 5. **OpenAI API Key**
- [ ] Required but not configured
- [ ] Needed for chat functionality
- **Action:** Provide API key or disable for MVP

---

## 📋 PHASE 1: Environment Setup (2 hrs)
- [ ] Create production `.env` file
- [ ] Set all required variables
- [ ] Verify database connectivity
- [ ] Generate secure SECRET_KEY

## 📋 PHASE 2: Code Hardening (2 hrs)
- [ ] Remove debug console.logs
- [ ] Update CORS to accept production domain
- [ ] Enable Next.js production mode
- [ ] Remove stub data/test endpoints

## 📋 PHASE 3: Testing (3 hrs)
- [ ] Local e2e test: registration → login → upload → chat
- [ ] Verify all API responses production-ready
- [ ] Test error handling and edge cases

## 📋 PHASE 4: Build & Deploy (8 hrs)
- [ ] Build frontend: `next build && next start`
- [ ] Build backend Docker image (or prepare for deployment)
- [ ] Deploy backend to production
- [ ] Deploy frontend to production
- [ ] Configure HTTPS/SSL certificates
- [ ] Point domain to production servers

## 📋 PHASE 5: Production Validation (5 hrs)
- [ ] Smoke test production URLs
- [ ] Verify HTTPS working
- [ ] Full user flow test (register → upload → chat)
- [ ] Monitor logs for errors
- [ ] Final documentation

## 📋 PHASE 6: Post-Deployment (4 hrs)
- [ ] Set up monitoring/alerts
- [ ] Document production runbook
- [ ] Create incident response plan
- [ ] Hand off to ops/support

---

## ❓ NEED YOUR INPUT

**Before proceeding, answer these:**

1. **Deployment Platform?**
   - [ ] Heroku
   - [ ] AWS (EC2, ECS, Lambda)
   - [ ] Vercel (frontend only)
   - [ ] DigitalOcean
   - [ ] Custom VPS
   - [ ] Docker on server

2. **Production Domain?**
   - Example: `api.app.com` and `app.com`
   - Current: _______________

3. **Database Setup?**
   - [ ] Already running PostgreSQL on prod
   - [ ] Need to set up PostgreSQL
   - [ ] Using managed database (AWS RDS, Heroku Postgres)

4. **OpenAI API?**
   - [ ] Have API key, will provide
   - [ ] Use stub mode for MVP
   - [ ] Will add later

---

## 🎯 What I'll Do When You Answer

1. ✅ Fix CORS to support production domain
2. ✅ Generate secure configuration files
3. ✅ Remove all debug code
4. ✅ Create deployment scripts
5. ✅ Provide step-by-step deployment instructions
6. ✅ Run all critical tests
7. ✅ Validate production readiness

**Time remaining: ~23 hours**
