#!/bin/bash
# =============================================================================
# Build Docker Images Script
# =============================================================================
# Purpose: Build backend and frontend Docker images and load into Minikube
# Phase IV: Kubernetes Deployment with AI-Assisted DevOps
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_IMAGE="todo-backend:v1"
FRONTEND_IMAGE="todo-frontend:v1"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}Todo AI Chatbot - Build Docker Images${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# -----------------------------------------------------------------------------
# Step 1: Check if Minikube is running
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[1/5] Checking Minikube status...${NC}"
if ! minikube status &> /dev/null; then
    echo -e "${RED}Error: Minikube is not running${NC}"
    echo "Start Minikube with: minikube start --cpus=2 --memory=4096"
    exit 1
fi
echo -e "${GREEN}✓ Minikube is running${NC}"
echo ""

# -----------------------------------------------------------------------------
# Step 2: Build Backend Image
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[2/5] Building backend Docker image...${NC}"
cd "$PROJECT_ROOT/backend"

# Option 1: Standard Docker build
docker build -t "$BACKEND_IMAGE" .

# Option 2: Docker AI (Gordon) - Uncomment if you have Docker AI installed
# docker ai "Build this Dockerfile and tag it as $BACKEND_IMAGE"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Backend image built successfully${NC}"
else
    echo -e "${RED}✗ Backend image build failed${NC}"
    exit 1
fi
echo ""

# -----------------------------------------------------------------------------
# Step 3: Build Frontend Image
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[3/5] Building frontend Docker image...${NC}"
cd "$PROJECT_ROOT/frontend"

# Option 1: Standard Docker build
docker build -t "$FRONTEND_IMAGE" .

# Option 2: Docker AI (Gordon) - Uncomment if you have Docker AI installed
# docker ai "Build this Dockerfile and tag it as $FRONTEND_IMAGE"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Frontend image built successfully${NC}"
else
    echo -e "${RED}✗ Frontend image build failed${NC}"
    exit 1
fi
echo ""

# -----------------------------------------------------------------------------
# Step 4: Load Images into Minikube
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[4/5] Loading images into Minikube...${NC}"

echo "Loading backend image..."
minikube image load "$BACKEND_IMAGE"

echo "Loading frontend image..."
minikube image load "$FRONTEND_IMAGE"

echo -e "${GREEN}✓ Images loaded into Minikube${NC}"
echo ""

# -----------------------------------------------------------------------------
# Step 5: Verify Images
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[5/5] Verifying images in Minikube...${NC}"

echo "Images in Minikube:"
minikube image ls | grep todo || echo "No todo images found"
echo ""

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}Build Complete!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "Built images:"
echo "  - $BACKEND_IMAGE"
echo "  - $FRONTEND_IMAGE"
echo ""
echo "Next steps:"
echo "  1. Create secrets: ./scripts/create-secrets.sh"
echo "  2. Deploy to Minikube: ./scripts/deploy-minikube.sh"
echo ""

# =============================================================================
# Docker AI (Gordon) Alternative Commands:
# =============================================================================
# If you have Docker AI installed, you can use these commands instead:
#
# Generate optimized Dockerfile:
#   docker ai "Create an optimized production Dockerfile for FastAPI"
#
# Build with best practices:
#   docker ai "Build backend/Dockerfile with security best practices"
#
# Optimize image size:
#   docker ai "Reduce the size of todo-backend:v1 image"
# =============================================================================
