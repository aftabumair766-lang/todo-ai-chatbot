"""Scheduler Service - Handles recurring tasks and reminders"""
import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dapr.ext.fastapi import DaprApp

# Add common library to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))

from dapr.state import DaprStateStore
from dapr.bindings import DaprBindings

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
STATE_STORE_NAME = "statestore"
CRON_BINDING_NAME = "cron-binding"

# Global Dapr clients (initialized in lifespan)
state_store: DaprStateStore = None
bindings: DaprBindings = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI app"""
    global state_store, bindings

    # Startup
    print(f"🚀 Scheduler Service starting in {ENVIRONMENT} mode")
    print(f"📡 Dapr HTTP port: {DAPR_HTTP_PORT}")

    # Initialize Dapr clients
    state_store = DaprStateStore(store_name=STATE_STORE_NAME)
    bindings = DaprBindings()

    print("✅ Dapr State Store initialized")
    print("✅ Dapr Bindings initialized")
    print(f"⏰ Cron binding: {CRON_BINDING_NAME}")

    yield

    # Shutdown
    print("🧹 Closing Dapr clients")
    if state_store:
        state_store.close()
    if bindings:
        bindings.close()
    print("👋 Scheduler Service shutting down")


# Create FastAPI app
app = FastAPI(
    title="Scheduler Service",
    description="Recurring Tasks and Reminders Scheduling",
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
        "service": "scheduler-service",
        "version": "1.0.0",
        "environment": ENVIRONMENT,
        "dapr": {
            "state_store": STATE_STORE_NAME,
            "cron_binding": CRON_BINDING_NAME
        }
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Scheduler Service",
        "version": "1.0.0",
        "features": {
            "recurring_tasks": "Phase 4 (US2)",
            "reminders": "Phase 5 (US3)"
        }
    }


# Cron binding subscription
@DaprBindings.subscribe_to_binding(dapr_app, CRON_BINDING_NAME)
async def handle_cron_trigger(data: dict):
    """
    Handle cron trigger every 1 minute.

    This will:
    - Generate recurring task instances (Phase 4)
    - Check and trigger pending reminders (Phase 5)
    """
    print(f"⏰ Cron trigger received at {data.get('time', 'unknown')}")

    # TODO: Implement recurring task generation (Phase 4, US2)
    # TODO: Implement reminder triggering (Phase 5, US3)

    return {"status": "processed"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=ENVIRONMENT == "development"
    )
