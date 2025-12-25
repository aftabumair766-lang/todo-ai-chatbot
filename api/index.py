"""
Vercel Serverless Function - Minimal Working Version
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(title="Todo AI Chatbot API")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Todo AI Chatbot API",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "todo-ai-chatbot",
        "version": "1.0.0"
    }

# Import and include auth routes
try:
    from backend.api import auth
    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
except Exception as e:
    print(f"Warning: Could not load auth routes: {e}")

# Import and include chat routes
try:
    from backend.api import chat
    app.include_router(chat.router, prefix="/api", tags=["chat"])
except Exception as e:
    print(f"Warning: Could not load chat routes: {e}")
