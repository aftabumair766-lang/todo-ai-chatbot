# 🚀 Deployment Guide

Complete guide for deploying Todo AI Chatbot to production.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Local Production Setup](#local-production-setup)
- [Database Migrations](#database-migrations)
- [Deploy to Cloud](#deploy-to-cloud)
- [Environment Configuration](#environment-configuration)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before deploying, ensure you have:

- [ ] Neon PostgreSQL database
- [ ] OpenAI API key with sufficient credits
- [ ] Redis instance (Upstash or Redis Cloud)
- [ ] Better Auth configured
- [ ] Domain name (for production)
- [ ] SSL certificate (automatic with Vercel/Netlify)

---

## Local Production Setup

### 1. Build Backend

```bash
cd backend

# Install production dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Test production build
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### 2. Build Frontend

```bash
cd frontend

# Install dependencies
npm ci  # Clean install for production

# Build
npm run build

# Test production build
npm run preview
```

---

## Database Migrations

### Create Migration

```bash
cd backend

# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add new column to tasks"

# Or create empty migration
alembic revision -m "Custom migration"

# Edit generated file in alembic/versions/
# Verify upgrade() and downgrade() functions
```

### Apply Migrations

```bash
# Show current version
alembic current

# Show migration history
alembic history

# Upgrade to latest
alembic upgrade head

# Upgrade to specific version
alembic upgrade abc123

# Rollback one version
alembic downgrade -1

# Rollback to specific version
alembic downgrade abc123
```

### Migration Best Practices

1. **Always test migrations locally first**
   ```bash
   # Test upgrade
   alembic upgrade head

   # Test downgrade
   alembic downgrade -1

   # Re-upgrade
   alembic upgrade head
   ```

2. **Backup database before production migrations**
   ```bash
   # Neon: Use branch feature
   # Or pg_dump
   pg_dump $DATABASE_URL > backup_$(date +%Y%m%d).sql
   ```

3. **Run migrations during low-traffic periods**

4. **Have rollback plan ready**

---

## Deploy to Cloud

### Option 1: Railway (Easiest)

**Backend:**

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Create project
railway init

# 4. Add PostgreSQL
railway add --plugin postgresql

# 5. Add Redis
railway add --plugin redis

# 6. Set environment variables
railway variables set OPENAI_API_KEY=sk-...
railway variables set BETTER_AUTH_SECRET=...
railway variables set BETTER_AUTH_ISSUER=https://auth.yourdomain.com

# 7. Deploy
railway up
```

**Frontend:**

```bash
# Deploy to Vercel
cd frontend
vercel deploy --prod

# Set environment variable
vercel env add VITE_API_URL https://your-backend.railway.app
```

---

### Option 2: Fly.io

**Create `fly.toml`:**

```toml
app = "todo-chatbot"
primary_region = "sjc"

[build]
  builder = "paketobuildpacks/builder:base"
  buildpacks = ["gcr.io/paketo-buildpacks/python"]

[env]
  PORT = "8000"

[[services]]
  http_checks = []
  internal_port = 8000
  processes = ["app"]
  protocol = "tcp"

  [[services.ports]]
    force_https = true
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443
```

**Deploy:**

```bash
# Login
fly auth login

# Create app
fly launch

# Set secrets
fly secrets set OPENAI_API_KEY=sk-...
fly secrets set DATABASE_URL=postgresql://...
fly secrets set REDIS_URL=redis://...

# Deploy
fly deploy

# Open app
fly open
```

---

### Option 3: Docker

**Create `Dockerfile`:**

```dockerfile
# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run migrations and start server
CMD alembic upgrade head && \
    uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

**Create `docker-compose.yml`:**

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/tododb
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - db
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_URL=http://localhost:8000

  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=tododb
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

**Deploy:**

```bash
# Build
docker-compose build

# Run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## Environment Configuration

### Production Environment Variables

```bash
# backend/.env.production

# Database (Neon Production)
DATABASE_URL=postgresql+asyncpg://user:pass@production.neon.tech/tododb

# OpenAI (Production API key)
OPENAI_API_KEY=sk-proj-production-key

# Better Auth
BETTER_AUTH_SECRET=secure-32-char-production-secret
BETTER_AUTH_ISSUER=https://auth.yourdomain.com

# Redis (Production)
REDIS_URL=redis://production-redis.upstash.io:6379

# Application
ENVIRONMENT=production
LOG_LEVEL=WARNING
CORS_ORIGINS=https://yourdomain.com
RATE_LIMIT_PER_MINUTE=100

# Security
ALLOWED_HOSTS=yourdomain.com,api.yourdomain.com
```

### Frontend Environment

```bash
# frontend/.env.production
VITE_API_URL=https://api.yourdomain.com
```

---

## Monitoring

### Application Logs

**Backend:**

```bash
# Railway
railway logs

# Fly.io
fly logs

# Docker
docker logs <container_id>
```

**Frontend:**

```bash
# Vercel
vercel logs

# Check browser console for errors
```

### Health Checks

```bash
# Backend health
curl https://api.yourdomain.com/health

# Expected response
{
  "status": "healthy",
  "service": "todo-ai-chatbot",
  "version": "1.0.0"
}
```

### Performance Monitoring

**Add Sentry (optional):**

```bash
pip install sentry-sdk[fastapi]
```

```python
# backend/main.py
import sentry_sdk

sentry_sdk.init(
    dsn="https://...@sentry.io/...",
    environment=settings.ENVIRONMENT,
    traces_sample_rate=0.1
)
```

---

## Troubleshooting

### Database Connection Issues

```bash
# Test connection
psql $DATABASE_URL -c "SELECT 1"

# Check connection pool
# In Python
from backend.db.session import engine
print(engine.pool.status())
```

### OpenAI Rate Limits

```bash
# Check usage
# https://platform.openai.com/account/usage

# Add retry logic in production
# backend/agents/todo_agent.py
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def call_openai(...):
    ...
```

### Redis Connection Issues

```bash
# Test Redis
redis-cli -u $REDIS_URL ping

# Check rate limiter
curl -I https://api.yourdomain.com/api/chat
# Look for: X-RateLimit-Remaining header
```

### CORS Errors

```python
# backend/config.py
CORS_ORIGINS="https://yourdomain.com,https://www.yourdomain.com"

# Restart backend after changes
```

---

## Security Checklist

- [ ] Use HTTPS everywhere
- [ ] Rotate secrets regularly
- [ ] Enable rate limiting
- [ ] Set secure CORS origins
- [ ] Use environment variables for secrets
- [ ] Enable database SSL
- [ ] Implement request logging
- [ ] Add API key rotation
- [ ] Set up monitoring/alerts
- [ ] Regular security audits

---

## Performance Optimization

### Database

```python
# Add indexes for common queries
# backend/alembic/versions/xxx_add_indexes.py

def upgrade():
    op.create_index('ix_messages_created_at', 'messages', ['created_at'])
    op.create_index('ix_tasks_user_id_completed', 'tasks', ['user_id', 'completed'])
```

### Caching

```python
# Add Redis caching for frequent queries
from redis import asyncio as aioredis

cache = aioredis.from_url(settings.REDIS_URL)

async def get_tasks_cached(user_id):
    key = f"tasks:{user_id}"
    cached = await cache.get(key)
    if cached:
        return json.loads(cached)

    tasks = await list_tasks(db, user_id)
    await cache.setex(key, 60, json.dumps(tasks))
    return tasks
```

### Connection Pooling

```python
# backend/db/session.py
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,  # Increase for production
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600  # Recycle connections hourly
)
```

---

## Backup & Recovery

### Database Backups

```bash
# Neon: Automatic backups + branch feature
# Manual backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore
psql $DATABASE_URL < backup_20251214_120000.sql
```

### Disaster Recovery Plan

1. **Database Failure**:
   - Restore from Neon automatic backup
   - Point-in-time recovery available

2. **Application Failure**:
   - Railway/Fly.io: Automatic restart
   - Docker: `docker-compose restart`

3. **Data Loss**:
   - Restore from daily backups
   - Check Neon branch history

---

## Scaling

### Horizontal Scaling

```bash
# Railway: Scale instances
railway scale --instances 3

# Fly.io: Scale regions
fly scale count 3
fly regions add ams,syd
```

### Load Balancing

```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      replicas: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    # Load balance across backend replicas
```

---

## Maintenance

### Regular Tasks

- [ ] Weekly: Review logs for errors
- [ ] Monthly: Update dependencies
- [ ] Monthly: Review OpenAI usage/costs
- [ ] Quarterly: Security audit
- [ ] Quarterly: Performance review

### Update Dependencies

```bash
# Backend
pip install -U -r requirements.txt
pip freeze > requirements.txt

# Frontend
npm update
npm audit fix

# Test after updates
pytest
npm run build
```

---

## Production Checklist

Before going live:

- [ ] All tests passing
- [ ] Migrations applied
- [ ] Environment variables configured
- [ ] HTTPS enabled
- [ ] CORS configured correctly
- [ ] Rate limiting enabled
- [ ] Monitoring setup
- [ ] Backup strategy in place
- [ ] Error tracking configured
- [ ] Documentation updated
- [ ] Load testing completed
- [ ] Security audit passed

---

**Your Todo AI Chatbot is production-ready!** 🎉
