# =============================================================================
# Todo AI Chatbot - Backend Dockerfile
# =============================================================================
# Multi-stage build for production-ready FastAPI application
# Phase IV: Kubernetes Deployment with AI-Assisted DevOps
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder - Install dependencies
# -----------------------------------------------------------------------------
FROM python:3.11-slim as builder

LABEL maintainer="Umair <umair@todo-chatbot.com>"
LABEL description="Todo AI Chatbot Backend - FastAPI with OpenAI GPT-4"

# Set working directory
WORKDIR /app

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies to user directory (no root required)
# --no-cache-dir: Don't cache packages (reduces image size)
# --user: Install to user directory (~/.local)
RUN pip install --no-cache-dir --user -r requirements.txt

# -----------------------------------------------------------------------------
# Stage 2: Production - Minimal runtime image
# -----------------------------------------------------------------------------
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY . .

# Add user packages to PATH
ENV PATH=/root/.local/bin:$PATH

# Set Python environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Expose port for FastAPI application
EXPOSE 8000

# Health check - calls /health endpoint every 30s
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run uvicorn server
# --host 0.0.0.0: Listen on all interfaces (required for containers)
# --port 8000: Default port for backend
# --workers 1: Single worker (can be scaled via Kubernetes replicas)
# Use simple backend for Phase IV demo (no complex dependencies)
CMD ["uvicorn", "main_simple:app", "--host", "0.0.0.0", "--port", "8000"]
# For full backend: CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# =============================================================================
# Image Build Instructions:
# =============================================================================
# Standard Docker CLI:
#   docker build -t todo-backend:v1 .
#   docker run -p 8000:8000 --env-file .env todo-backend:v1
#
# Docker AI (Gordon):
#   docker ai "Build this Dockerfile and tag it as todo-backend:v1"
#   docker ai "Optimize this Dockerfile for smaller image size"
#
# For Minikube:
#   docker build -t todo-backend:v1 .
#   minikube image load todo-backend:v1
# =============================================================================
