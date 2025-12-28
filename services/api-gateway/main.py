"""API Gateway Service - Entry point for all client requests"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dapr.ext.fastapi import DaprApp

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI app"""
    # Startup
    print(f"🚀 API Gateway starting in {ENVIRONMENT} mode")
    print(f"📡 Dapr HTTP port: {DAPR_HTTP_PORT}")

    yield

    # Shutdown
    print("👋 API Gateway shutting down")


# Create FastAPI app
app = FastAPI(
    title="Todo Chatbot API Gateway",
    description="Cloud-Native Event-Driven Todo Chatbot - API Gateway Service",
    version="1.0.0",
    lifespan=lifespan
)

# Create Dapr app
dapr_app = DaprApp(app)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on environment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes probes"""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "version": "1.0.0",
        "environment": ENVIRONMENT
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Todo Chatbot API Gateway",
        "version": "1.0.0",
        "docs": "/docs"
    }


# TODO: Add chat endpoint after implementing JWT auth (T033)
# TODO: Integrate with Task Service via Dapr service invocation

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=ENVIRONMENT == "development"
    )
