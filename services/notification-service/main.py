"""Notification Service - Handles email notifications for reminders"""
import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from dapr.ext.fastapi import DaprApp

# Add common library to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))

from dapr.bindings import DaprBindings
from dapr.pubsub import DaprPubSub

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
PUBSUB_NAME = "pubsub"
EMAIL_BINDING_NAME = "email-binding"

# Global Dapr clients (initialized in lifespan)
pubsub: DaprPubSub = None
bindings: DaprBindings = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI app"""
    global pubsub, bindings

    # Startup
    print(f"🚀 Notification Service starting in {ENVIRONMENT} mode")
    print(f"📡 Dapr HTTP port: {DAPR_HTTP_PORT}")

    # Initialize Dapr clients
    pubsub = DaprPubSub(pubsub_name=PUBSUB_NAME)
    bindings = DaprBindings()

    print("✅ Dapr Pub/Sub initialized")
    print("✅ Dapr Bindings initialized")
    print(f"📧 Email binding: {EMAIL_BINDING_NAME}")

    yield

    # Shutdown
    print("🧹 Closing Dapr clients")
    if pubsub:
        pubsub.close()
    if bindings:
        bindings.close()
    print("👋 Notification Service shutting down")


# Create FastAPI app
app = FastAPI(
    title="Notification Service",
    description="Email Notifications for Task Reminders",
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
        "service": "notification-service",
        "version": "1.0.0",
        "environment": ENVIRONMENT,
        "dapr": {
            "pubsub": PUBSUB_NAME,
            "email_binding": EMAIL_BINDING_NAME
        }
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Notification Service",
        "version": "1.0.0",
        "features": {
            "email_notifications": "Phase 5 (US3)"
        }
    }


# Subscribe to reminder.triggered events
@DaprPubSub.subscribe(dapr_app, PUBSUB_NAME, "reminder.triggered")
async def handle_reminder_triggered(event_data: dict):
    """
    Handle reminder.triggered events from Kafka.

    Sends email notification via SendGrid binding.
    """
    print(f"📬 Received reminder.triggered event: {event_data}")

    # TODO: Implement email notification (Phase 5, US3)
    # Extract reminder data
    # Send email via bindings.send_email()

    return {"status": "processed"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=ENVIRONMENT == "development"
    )
