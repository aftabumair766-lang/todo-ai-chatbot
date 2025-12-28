"""Task Service - Handles task CRUD operations with Dapr State Store"""
import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dapr.ext.fastapi import DaprApp

# Add common library to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))

from dapr.state import DaprStateStore
from dapr.pubsub import DaprPubSub

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
STATE_STORE_NAME = "statestore"
PUBSUB_NAME = "pubsub"

# Global Dapr clients (initialized in lifespan)
state_store: DaprStateStore = None
pubsub: DaprPubSub = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI app"""
    global state_store, pubsub

    # Startup
    print(f"🚀 Task Service starting in {ENVIRONMENT} mode")
    print(f"📡 Dapr HTTP port: {DAPR_HTTP_PORT}")

    # Initialize Dapr clients
    state_store = DaprStateStore(store_name=STATE_STORE_NAME)
    pubsub = DaprPubSub(pubsub_name=PUBSUB_NAME)

    print("✅ Dapr State Store initialized")
    print("✅ Dapr Pub/Sub initialized")

    yield

    # Shutdown
    print("🧹 Closing Dapr clients")
    if state_store:
        state_store.close()
    if pubsub:
        pubsub.close()
    print("👋 Task Service shutting down")


# Create FastAPI app
app = FastAPI(
    title="Task Service",
    description="Cloud-Native Task Management with Dapr State Store",
    version="1.0.0",
    lifespan=lifespan
)

# Create Dapr app
dapr_app = DaprApp(app)


@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes probes"""
    return {
        "status": "healthy",
        "service": "task-service",
        "version": "1.0.0",
        "environment": ENVIRONMENT,
        "dapr": {
            "state_store": STATE_STORE_NAME,
            "pubsub": PUBSUB_NAME
        }
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Task Service",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "tasks": "/tasks (TODO: T035)"
        }
    }


# Import task CRUD router
from handlers import task_crud

# Initialize task CRUD router with state store (done after lifespan startup)
task_crud.init_router(state_store)

# Include task CRUD router
app.include_router(task_crud.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=ENVIRONMENT == "development"
    )
