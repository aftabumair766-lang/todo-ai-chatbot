# =============================================================================
# Todo AI Chatbot - Frontend Dockerfile
# =============================================================================
# Multi-stage build for production-ready React application with Nginx
# Phase IV: Kubernetes Deployment with AI-Assisted DevOps
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder - Build React application
# -----------------------------------------------------------------------------
FROM node:18 as builder

LABEL maintainer="Umair <umair@todo-chatbot.com>"
LABEL description="Todo AI Chatbot Frontend - React with TypeScript"

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
# npm ci: Clean install (faster and more reliable than npm install)
RUN npm ci

# Copy application source code
COPY . .

# Build production bundle
# This creates optimized static files in /app/dist
RUN npm run build

# -----------------------------------------------------------------------------
# Stage 2: Production - Serve with Nginx
# -----------------------------------------------------------------------------
FROM nginx:alpine

# Copy built files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration
# This enables React Router support (SPA routing)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80 for HTTP traffic
EXPOSE 80

# Health check - verify Nginx is serving content
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# Start Nginx in foreground mode
# -g daemon off: Required for Docker (keeps container running)
CMD ["nginx", "-g", "daemon off;"]

# =============================================================================
# Image Build Instructions:
# =============================================================================
# Standard Docker CLI:
#   docker build -t todo-frontend:v1 .
#   docker run -p 80:80 todo-frontend:v1
#
# Docker AI (Gordon):
#   docker ai "Build this Dockerfile and tag it as todo-frontend:v1"
#   docker ai "Optimize this Dockerfile for production deployment"
#
# For Minikube:
#   docker build -t todo-frontend:v1 .
#   minikube image load todo-frontend:v1
#
# Image Size Optimization:
#   - Stage 1 (builder): ~1.2GB (Node.js + dependencies + build)
#   - Stage 2 (production): ~25MB (Nginx Alpine + static files)
#   - Final image: Only stage 2 is kept (~25MB)
# =============================================================================
