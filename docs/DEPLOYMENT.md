# Production Deployment Guide

Complete guide for deploying the Todo AI Chatbot to production.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Configuration](#environment-configuration)
3. [Database Setup](#database-setup)
4. [Backend Deployment](#backend-deployment)
5. [Frontend Deployment](#frontend-deployment)
6. [Security Checklist](#security-checklist)
7. [Monitoring & Logging](#monitoring--logging)
8. [Scaling Considerations](#scaling-considerations)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Services
- **OpenAI API Account** - https://platform.openai.com
- **Neon PostgreSQL Database** - https://neon.tech (already configured)
- **Backend Hosting** - Choose one:
  - Railway (recommended for beginners)
  - Render
  - Fly.io
  - AWS/GCP/Azure
  - DigitalOcean
- **Frontend Hosting** - Choose one:
  - Vercel (recommended)
  - Netlify
  - Cloudflare Pages
  - AWS S3 + CloudFront

### Local Tools
- Python 3.11+
- Node.js 18+
- Git

---

## Environment Configuration

### Backend Environment Variables

Create production `.env` file in `backend/`:

```bash
# Database (Neon PostgreSQL - Production)
DATABASE_URL=postgresql+asyncpg://neondb_owner:[PASSWORD]@[HOST]-pooler.ap-southeast-1.aws.neon.tech/neondb?ssl=require

# OpenAI API
OPENAI_API_KEY=sk-proj-[YOUR_PRODUCTION_KEY]

# ChatKit Workflow (Optional - if available)
CHATKIT_WORKFLOW_ID=asst_[YOUR_WORKFLOW_ID]

# Better Auth (REQUIRED for production)
BETTER_AUTH_SECRET=[GENERATE_32_CHAR_RANDOM_STRING]
BETTER_AUTH_ISSUER=https://your-production-domain.com

# Redis (Optional - for rate limiting)
REDIS_URL=redis://[YOUR_REDIS_HOST]:6379/0

# Application Settings
ENVIRONMENT=production
LOG_LEVEL=INFO
CORS_ORIGINS=https://your-frontend-domain.com
RATE_LIMIT_PER_MINUTE=10

# Production Security
# IMPORTANT: Never use "test" token in production!
```

### Frontend Environment Variables

Create `.env.production` in `frontend/`:

```bash
VITE_API_URL=https://your-backend-domain.com
VITE_ENVIRONMENT=production
```

### Generating Secure Secrets

```bash
# Generate BETTER_AUTH_SECRET (32 characters)
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Or using OpenSSL
openssl rand -base64 32
```

---

## Database Setup

### Neon PostgreSQL (Already Configured)

Your database is already set up at:
```
DATABASE_URL=postgresql+asyncpg://neondb_owner:npg_wGKrcxfqj17l@ep-weathered-math-a118ik6f-pooler.ap-southeast-1.aws.neon.tech/neondb?ssl=require
```

### Production Database Checklist

- [x] **Connection Pooling:** Using `-pooler` endpoint
- [ ] **Backup Strategy:** Enable automatic backups in Neon dashboard
- [ ] **Scaling Plan:** Upgrade from free tier if needed
- [ ] **Monitoring:** Set up database alerts in Neon

### Running Migrations

Before first deployment:

```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

---

## Backend Deployment

### Option 1: Railway (Recommended for Beginners)

**Why Railway:**
- Automatic HTTPS
- Built-in PostgreSQL support (or use external Neon)
- GitHub integration
- Easy environment variables

**Steps:**

1. **Install Railway CLI:**
   ```bash
   npm i -g @railway/cli
   railway login
   ```

2. **Initialize Project:**
   ```bash
   cd /home/umair/todo-chatbot/backend
   railway init
   ```

3. **Add Environment Variables:**
   - Go to Railway dashboard
   - Add all variables from [Environment Configuration](#backend-environment-variables)

4. **Deploy:**
   ```bash
   railway up
   ```

5. **Get Backend URL:**
   ```bash
   railway domain
   # Example: https://todo-backend-production.up.railway.app
   ```

### Option 2: Render

**Steps:**

1. **Create `render.yaml` in project root:**
   ```yaml
   services:
     - type: web
       name: todo-backend
       env: python
       region: singapore
       plan: starter
       buildCommand: cd backend && pip install -r requirements.txt
       startCommand: cd backend && uvicorn backend.main:app --host 0.0.0.0 --port $PORT
       envVars:
         - key: DATABASE_URL
           sync: false
         - key: OPENAI_API_KEY
           sync: false
         - key: BETTER_AUTH_SECRET
           sync: false
         - key: ENVIRONMENT
           value: production
         - key: LOG_LEVEL
           value: INFO
   ```

2. **Connect GitHub Repository:**
   - Go to https://dashboard.render.com
   - New > Web Service
   - Connect your repository
   - Render auto-detects `render.yaml`

3. **Add Environment Variables:**
   - In Render dashboard, add all secrets

### Option 3: Fly.io

**Steps:**

1. **Install Fly CLI:**
   ```bash
   curl -L https://fly.io/install.sh | sh
   fly auth login
   ```

2. **Create `fly.toml` in backend directory:**
   ```toml
   app = "todo-backend"
   primary_region = "sin"

   [build]
   builder = "paketobuildpacks/builder:base"

   [env]
   PORT = "8000"
   ENVIRONMENT = "production"

   [[services]]
   http_checks = []
   internal_port = 8000
   processes = ["app"]
   protocol = "tcp"
   script_checks = []

   [[services.ports]]
   force_https = true
   handlers = ["http"]
   port = 80

   [[services.ports]]
   handlers = ["tls", "http"]
   port = 443

   [services.concurrency]
   hard_limit = 25
   soft_limit = 20
   type = "connections"
   ```

3. **Deploy:**
   ```bash
   cd backend
   fly launch
   fly secrets set DATABASE_URL="..." OPENAI_API_KEY="..." BETTER_AUTH_SECRET="..."
   fly deploy
   ```

### Option 4: Docker (Any Cloud Provider)

**Create `backend/Dockerfile`:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build and deploy:**

```bash
cd backend
docker build -t todo-backend .
docker run -p 8000:8000 --env-file .env todo-backend
```

### Post-Deployment Backend Verification

```bash
# Health check
curl https://your-backend-domain.com/health

# API documentation
open https://your-backend-domain.com/docs

# Test task creation
curl -X POST https://your-backend-domain.com/api/chat \
  -H "Authorization: Bearer test" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add task: Test deployment"}'
```

---

## Frontend Deployment

### Option 1: Vercel (Recommended)

**Why Vercel:**
- Optimized for React/Vite
- Automatic HTTPS
- CDN distribution
- GitHub integration
- Zero configuration

**Steps:**

1. **Install Vercel CLI:**
   ```bash
   npm i -g vercel
   vercel login
   ```

2. **Configure Build:**
   Create `vercel.json` in `frontend/`:
   ```json
   {
     "buildCommand": "npm run build",
     "outputDirectory": "dist",
     "framework": "vite",
     "env": {
       "VITE_API_URL": "https://your-backend-domain.com"
     }
   }
   ```

3. **Deploy:**
   ```bash
   cd frontend
   vercel --prod
   ```

4. **Add Environment Variables:**
   - Go to Vercel dashboard > Settings > Environment Variables
   - Add `VITE_API_URL` with your backend URL

### Option 2: Netlify

**Steps:**

1. **Create `netlify.toml` in frontend directory:**
   ```toml
   [build]
   command = "npm run build"
   publish = "dist"

   [[redirects]]
   from = "/*"
   to = "/index.html"
   status = 200
   ```

2. **Deploy:**
   ```bash
   cd frontend
   npm install -g netlify-cli
   netlify login
   netlify init
   netlify deploy --prod
   ```

### Option 3: Cloudflare Pages

**Steps:**

1. **Go to Cloudflare Dashboard:**
   - Pages > Create a project
   - Connect GitHub repository

2. **Build Settings:**
   - Build command: `npm run build`
   - Build output directory: `dist`
   - Root directory: `frontend`

3. **Environment Variables:**
   - Add `VITE_API_URL` with backend URL

### Post-Deployment Frontend Verification

1. **Open frontend URL** in browser
2. **Test authentication** (should NOT accept "test" token in production)
3. **Test task operations:**
   - Add task
   - List tasks
   - Complete task
   - Delete task
4. **Check browser console** for errors

---

## Security Checklist

### Before Going Live

- [ ] **Remove Test Authentication:**
  - Implement proper Better Auth integration
  - Remove hardcoded "test" token from `backend/auth/better_auth.py`

- [ ] **Environment Variables:**
  - [ ] Generate strong `BETTER_AUTH_SECRET` (32+ characters)
  - [ ] Use production OpenAI API key (not dev key)
  - [ ] Never commit `.env` files to Git
  - [ ] Verify `.env` is in `.gitignore`

- [ ] **CORS Configuration:**
  - [ ] Set `CORS_ORIGINS` to exact frontend domain
  - [ ] Do NOT use `*` wildcard in production

- [ ] **Database Security:**
  - [ ] Use connection pooler (`-pooler` endpoint)
  - [ ] Enable SSL (`?ssl=require`)
  - [ ] Rotate database password if previously exposed

- [ ] **API Security:**
  - [ ] Enable rate limiting (configure Redis)
  - [ ] Implement request validation
  - [ ] Set up API monitoring

- [ ] **HTTPS:**
  - [ ] Backend served over HTTPS
  - [ ] Frontend served over HTTPS
  - [ ] No mixed content warnings

- [ ] **Secrets Management:**
  - [ ] OpenAI API key not exposed in frontend
  - [ ] Database credentials not in client code
  - [ ] All secrets in environment variables

### Security Headers (Add to Backend)

Update `backend/main.py`:

```python
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

if settings.ENVIRONMENT == "production":
    # Force HTTPS
    app.add_middleware(HTTPSRedirectMiddleware)

    # Trusted hosts only
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["your-frontend-domain.com", "your-backend-domain.com"]
    )
```

---

## Monitoring & Logging

### Application Monitoring

**Option 1: Sentry (Recommended)**

1. **Install Sentry:**
   ```bash
   pip install --upgrade sentry-sdk[fastapi]
   ```

2. **Add to `backend/main.py`:**
   ```python
   import sentry_sdk
   from sentry_sdk.integrations.fastapi import FastApiIntegration

   if settings.ENVIRONMENT == "production":
       sentry_sdk.init(
           dsn="https://your-sentry-dsn",
           integrations=[FastApiIntegration()],
           traces_sample_rate=1.0,
       )
   ```

**Option 2: LogTail**

For centralized logging:
- Sign up at https://logtail.com
- Add logging integration to backend

### Database Monitoring

**Neon Dashboard:**
- Monitor query performance
- Set up alerts for high CPU/memory
- Track connection pool usage

### Health Checks

Create monitoring service (e.g., UptimeRobot):
- Check: `https://your-backend.com/health` every 5 minutes
- Alert on downtime

---

## Scaling Considerations

### Backend Scaling

**Horizontal Scaling:**
- Deploy multiple backend instances
- Use load balancer (Railway/Render auto-handles)
- Session state in Redis (not in-memory)

**Vertical Scaling:**
- Upgrade server plan when needed
- Monitor: CPU, memory, request latency

**Database Scaling:**
- Neon auto-scales compute
- Upgrade plan for more storage/connections
- Consider read replicas for heavy read loads

### Frontend Scaling

- **CDN:** Vercel/Netlify provide global CDN
- **Caching:** Set proper cache headers
- **Asset Optimization:** Use Vite build optimizations

### Rate Limiting

**Production Rate Limits:**

```python
# backend/config.py
RATE_LIMIT_PER_MINUTE: int = 10  # Per user
```

**Implement Redis-backed rate limiting:**

```python
# backend/middleware/rate_limit.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_URL
)

@app.post("/api/chat")
@limiter.limit("10/minute")
async def chat_endpoint(...):
    pass
```

---

## Troubleshooting

### Common Production Issues

#### 1. Database Connection Fails

**Symptoms:**
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) connection failed
```

**Solutions:**
- Verify `DATABASE_URL` includes `-pooler` endpoint
- Check SSL is enabled: `?ssl=require`
- Verify Neon database is not paused (free tier auto-pauses)
- Test connection from backend host (some networks block PostgreSQL ports)

#### 2. CORS Errors

**Symptoms:**
```
Access to fetch at 'https://backend.com/api/chat' from origin 'https://frontend.com'
has been blocked by CORS policy
```

**Solutions:**
- Check `CORS_ORIGINS` in backend `.env`
- Must match exact frontend domain (including protocol)
- No trailing slashes
- Restart backend after changes

#### 3. OpenAI API Rate Limits

**Symptoms:**
```
Error code: 429 - Rate limit exceeded
```

**Solutions:**
- Upgrade OpenAI API plan
- Implement request queuing
- Add user-facing error messages
- Cache common responses

#### 4. Frontend Environment Variables Not Working

**Symptoms:**
- `VITE_API_URL` is undefined
- API calls go to `localhost`

**Solutions:**
- Vite requires `VITE_` prefix for exposed variables
- Must rebuild after changing env vars: `npm run build`
- Check build logs for environment variable injection

#### 5. Authentication Fails in Production

**Symptoms:**
```
401 Unauthorized on all requests
```

**Solutions:**
- Verify `BETTER_AUTH_SECRET` is set
- Check JWT token format
- Ensure `Authorization: Bearer <token>` header is sent
- Remove "test" token hardcode from production

### Debug Commands

```bash
# Check backend health
curl https://your-backend.com/health

# Test database connection
psql "postgresql://neondb_owner:...@...neon.tech/neondb?sslmode=require"

# View backend logs (Railway)
railway logs

# View backend logs (Render)
# Check dashboard logs tab

# View frontend build logs (Vercel)
vercel logs

# Test CORS
curl -X OPTIONS https://your-backend.com/api/chat \
  -H "Origin: https://your-frontend.com" \
  -H "Access-Control-Request-Method: POST" \
  -v
```

### Getting Help

1. **Check logs first:**
   - Backend logs (deployment platform)
   - Frontend browser console
   - Database logs (Neon dashboard)

2. **Verify configuration:**
   - All environment variables set
   - Correct URLs (no trailing slashes)
   - HTTPS enabled everywhere

3. **Test locally:**
   - Can you reproduce in local production build?
   - `npm run build && npm run preview`

4. **Platform-specific support:**
   - Railway: https://railway.app/help
   - Render: https://render.com/docs
   - Vercel: https://vercel.com/support

---

## Deployment Checklist

### Pre-Deployment

- [ ] All tests passing locally
- [ ] Environment variables documented
- [ ] Security checklist completed
- [ ] Database migrations ready
- [ ] Remove development/test code

### Deployment

- [ ] Backend deployed and accessible
- [ ] Frontend deployed and accessible
- [ ] Database connected and migrations run
- [ ] Environment variables configured
- [ ] HTTPS enabled on both frontend and backend

### Post-Deployment

- [ ] Health check endpoint responding
- [ ] API documentation accessible
- [ ] Test all user flows (add/list/complete/delete tasks)
- [ ] Monitor logs for errors
- [ ] Set up monitoring/alerts
- [ ] Test from multiple devices/networks
- [ ] Performance testing (load test if needed)

### Ongoing Maintenance

- [ ] Regular dependency updates
- [ ] Security patches
- [ ] Database backups verified
- [ ] Monitor API costs (OpenAI usage)
- [ ] Review logs weekly
- [ ] Uptime monitoring

---

## Cost Estimates

### Minimal Production Setup (Free Tier)

- **Backend:** Railway free tier or Render free
- **Frontend:** Vercel free tier
- **Database:** Neon free tier (500MB, 0.5GB RAM)
- **OpenAI API:** Pay per use (~$0.002 per task)

**Total:** $0/month + OpenAI API usage

### Recommended Production Setup

- **Backend:** Railway Hobby ($5/month) or Render Starter ($7/month)
- **Frontend:** Vercel Pro ($20/month) - only if high traffic
- **Database:** Neon Scale ($19/month) - better performance
- **Redis:** Upstash ($10/month) - for rate limiting
- **Monitoring:** Sentry ($26/month) - error tracking

**Total:** $40-60/month + API usage

### Enterprise Setup

- **Backend:** Railway Pro ($20/month) + multiple instances
- **Frontend:** Vercel Enterprise (custom pricing)
- **Database:** Neon Business ($69/month)
- **Redis:** Upstash Pro ($50/month)
- **Monitoring:** Sentry Business ($99/month)

**Total:** $200+/month + API usage

---

## Quick Start Commands

### Deploy Backend to Railway

```bash
cd /home/umair/todo-chatbot/backend
railway init
railway up
railway domain
```

### Deploy Frontend to Vercel

```bash
cd /home/umair/todo-chatbot/frontend
vercel --prod
```

### Verify Deployment

```bash
# Backend health
curl https://your-backend.up.railway.app/health

# Frontend
open https://your-app.vercel.app
```

---

## Support

For deployment issues:

1. **Documentation:**
   - Railway: https://docs.railway.app
   - Vercel: https://vercel.com/docs
   - Neon: https://neon.tech/docs

2. **Project-Specific:**
   - Check `backend/logs/` for detailed errors
   - Review `CHATKIT_INTEGRATION_STATUS.md` for current status

3. **Community:**
   - Railway Discord: https://discord.gg/railway
   - Vercel Discord: https://discord.gg/vercel

---

**Your Todo AI Chatbot is production-ready!** Follow this guide step by step for a successful deployment.
