# Vercel Deployment Guide

## 📦 Deployment Requirements

### Backend (FastAPI)

1. **Push to GitHub** ✅ (Already done)

2. **Deploy to Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Sign in with GitHub
   - Click "Add New Project"
   - Import `todo-ai-chatbot` repository
   - Configure:
     - **Framework Preset:** Other
     - **Root Directory:** `./`
     - **Build Command:** Leave empty
     - **Output Directory:** Leave empty

3. **Environment Variables (IMPORTANT):**
   Add these in Vercel Project Settings → Environment Variables:
   ```
   DATABASE_URL=your_neon_postgres_url
   OPENAI_API_KEY=your_openai_key
   BETTER_AUTH_SECRET=your_secret_key
   BETTER_AUTH_ISSUER=your_app_name
   CORS_ORIGINS=*
   ```

4. **Deploy!**
   - Click "Deploy"
   - Wait for deployment
   - Get your backend URL: `https://your-project.vercel.app`

---

### Frontend (React + Vite)

1. **Create separate Vercel project for frontend:**
   - Go to [vercel.com](https://vercel.com)
   - Click "Add New Project"
   - Import same `todo-ai-chatbot` repository
   - Configure:
     - **Framework Preset:** Vite
     - **Root Directory:** `frontend`
     - **Build Command:** `npm run build`
     - **Output Directory:** `dist`

2. **Environment Variable:**
   ```
   VITE_API_URL=https://your-backend-project.vercel.app
   ```

3. **Deploy!**
   - Click "Deploy"
   - Get your frontend URL: `https://your-frontend.vercel.app`

---

## 📋 Submission Checklist

- [x] **GitHub Repo:** https://github.com/aftabumair766-lang/todo-ai-chatbot
- [ ] **Backend URL:** `https://your-backend.vercel.app`
- [ ] **Frontend URL:** `https://your-frontend.vercel.app`
- [ ] **Demo Video:** (90 seconds max)
- [ ] **WhatsApp Number:** Your contact

---

## 🎬 Demo Video Tips

Use **NotebookLM** or **Screen Recording**:

1. **Introduction (10 seconds)**
   - "Hi, this is the Todo AI Chatbot with Better Auth"

2. **Demo Features (70 seconds)**
   - Show registration/login
   - Show language selector (English, Urdu, Chinese)
   - Show neon theme
   - Create a todo task with AI
   - Show JWT authentication

3. **Tech Stack (10 seconds)**
   - "Built with FastAPI, React, OpenAI, Neon PostgreSQL, and Better Auth"

---

## ⚠️ Important Notes

1. **Neon PostgreSQL:** Make sure your DATABASE_URL is from Neon (serverless PostgreSQL)
2. **CORS:** Update CORS_ORIGINS in backend to your frontend URL after deployment
3. **OpenAI API:** Make sure you have credits in your OpenAI account
4. **Test locally first:** Verify everything works before deploying

---

## 🐛 Troubleshooting

**Backend 500 Error?**
- Check environment variables are set correctly
- Check Vercel logs for errors

**Frontend can't connect to backend?**
- Update VITE_API_URL to your Vercel backend URL
- Check CORS settings in backend

**Database connection error?**
- Verify DATABASE_URL is correct Neon connection string
- Check Neon database is active
