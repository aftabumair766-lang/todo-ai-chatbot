"""
FastAPI Application for Todo AI Chatbot

Main application entry point with CORS, rate limiting, and API routes.
Constitution Compliance: All 6 principles enforced at app level.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Rate limiting disabled for Vercel serverless deployment
# from slowapi import Limiter, _rate_limit_exceeded_handler
# from slowapi.util import get_remote_address
# from slowapi.errors import RateLimitExceeded
from backend.config import get_settings
# Database init removed for Vercel serverless (tables already exist in Neon)
# from backend.db.session import init_db, close_db
# MCP server initialization moved to lazy loading
# from backend.mcp.server import create_mcp_server
from backend.api import chat, chatkit, auth

logger = logging.getLogger(__name__)
settings = get_settings()


# ============================================================================
# Application Lifespan (Startup/Shutdown Events)
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager (simplified for Vercel).

    Vercel serverless functions don't support long-running startup tasks.
    Database initialization happens on first request instead.
    """
    # Startup - minimal initialization for Vercel
    logger.info("Starting Todo AI Chatbot application...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info("Application startup complete")

    yield

    # Shutdown - minimal cleanup
    logger.info("Shutting down application...")


# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="Todo AI Chatbot API",
    description="Natural language todo management powered by OpenAI Agents SDK and MCP",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)


# ============================================================================
# CORS Middleware
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # Already parsed as list in config.py
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Rate Limiting (Disabled for Vercel Serverless)
# ============================================================================

# Rate limiting disabled for Vercel serverless deployment
# Vercel has built-in DDoS protection and rate limiting
# limiter = Limiter(
#     key_func=get_remote_address,
#     storage_uri=settings.REDIS_URL,
#     default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"],
# )
# app.state.limiter = limiter
# app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ============================================================================
# API Routes
# ============================================================================

# Include authentication endpoints (public - no auth required)
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

# Include chat endpoint
app.include_router(chat.router, prefix="/api", tags=["chat"])

# Include ChatKit session endpoint
app.include_router(chatkit.router, prefix="/api", tags=["chatkit"])


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health", tags=["health"])
async def health_check():
    """
    Health check endpoint.

    Returns:
        dict: Service status and version
    """
    return {
        "status": "healthy",
        "service": "todo-ai-chatbot",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint.

    Returns:
        dict: Welcome message
    """
    return {
        "message": "Todo AI Chatbot API",
        "docs": "/docs",
        "health": "/health",
    }


# ============================================================================
# Application Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower(),
    )
