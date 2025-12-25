#!/bin/bash
# =============================================================================
# Deploy to Minikube Script
# =============================================================================
# Purpose: Deploy Todo AI Chatbot to Minikube using Helm charts
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
NAMESPACE="todo-app"
BACKEND_RELEASE="todo-backend"
FRONTEND_RELEASE="todo-frontend"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}Todo AI Chatbot - Deploy to Minikube${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# -----------------------------------------------------------------------------
# Step 1: Check Prerequisites
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[1/8] Checking prerequisites...${NC}"

# Check Minikube
if ! minikube status &> /dev/null; then
    echo -e "${RED}Error: Minikube is not running${NC}"
    echo "Start Minikube with: minikube start --cpus=2 --memory=4096"
    exit 1
fi

# Check Helm
if ! command -v helm &> /dev/null; then
    echo -e "${RED}Error: Helm is not installed${NC}"
    echo "Install Helm: https://helm.sh/docs/intro/install/"
    exit 1
fi

# Check if .env file exists
if [ ! -f "$PROJECT_ROOT/backend/.env" ]; then
    echo -e "${RED}Error: backend/.env file not found${NC}"
    echo "Create .env file with required secrets (OPENAI_API_KEY, DATABASE_URL, etc.)"
    exit 1
fi

echo -e "${GREEN}✓ Prerequisites check passed${NC}"
echo ""

# -----------------------------------------------------------------------------
# Step 2: Create Namespace
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[2/8] Creating namespace...${NC}"
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
echo -e "${GREEN}✓ Namespace '$NAMESPACE' ready${NC}"
echo ""

# -----------------------------------------------------------------------------
# Step 3: Create Secrets from .env file
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[3/8] Creating Kubernetes secrets...${NC}"

# Source the .env file
source "$PROJECT_ROOT/backend/.env"

# Create secret for backend
kubectl create secret generic "$BACKEND_RELEASE-secrets" \
  --from-literal=openai-api-key="$OPENAI_API_KEY" \
  --from-literal=database-url="$DATABASE_URL" \
  --from-literal=better-auth-secret="${BETTER_AUTH_SECRET:-changeme123456789012345678901234}" \
  --from-literal=better-auth-issuer="${BETTER_AUTH_ISSUER:-http://localhost:8000}" \
  --namespace="$NAMESPACE" \
  --dry-run=client -o yaml | kubectl apply -f -

echo -e "${GREEN}✓ Secrets created${NC}"
echo ""

# -----------------------------------------------------------------------------
# Step 4: Deploy Backend with Helm
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[4/8] Deploying backend...${NC}"

helm upgrade --install "$BACKEND_RELEASE" "$PROJECT_ROOT/helm/todo-backend" \
  --namespace="$NAMESPACE" \
  --set image.pullPolicy=Never \
  --wait

echo -e "${GREEN}✓ Backend deployed${NC}"
echo ""

# -----------------------------------------------------------------------------
# Step 5: Wait for Backend to be Ready
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[5/8] Waiting for backend to be ready...${NC}"
kubectl wait --for=condition=available --timeout=120s \
  deployment/"$BACKEND_RELEASE" -n "$NAMESPACE"
echo -e "${GREEN}✓ Backend is ready${NC}"
echo ""

# -----------------------------------------------------------------------------
# Step 6: Deploy Frontend with Helm
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[6/8] Deploying frontend...${NC}"

helm upgrade --install "$FRONTEND_RELEASE" "$PROJECT_ROOT/helm/todo-frontend" \
  --namespace="$NAMESPACE" \
  --set image.pullPolicy=Never \
  --set env.VITE_API_URL="http://$BACKEND_RELEASE:8000" \
  --wait

echo -e "${GREEN}✓ Frontend deployed${NC}"
echo ""

# -----------------------------------------------------------------------------
# Step 7: Wait for Frontend to be Ready
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[7/8] Waiting for frontend to be ready...${NC}"
kubectl wait --for=condition=available --timeout=120s \
  deployment/"$FRONTEND_RELEASE" -n "$NAMESPACE"
echo -e "${GREEN}✓ Frontend is ready${NC}"
echo ""

# -----------------------------------------------------------------------------
# Step 8: Display Access Information
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[8/8] Getting access information...${NC}"

# Get frontend URL
FRONTEND_URL=$(minikube service "$FRONTEND_RELEASE" -n "$NAMESPACE" --url 2>/dev/null || echo "Not available")

# Get pod status
echo ""
echo "Pod Status:"
kubectl get pods -n "$NAMESPACE"

echo ""
echo "Services:"
kubectl get svc -n "$NAMESPACE"

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "Access the application:"
echo -e "  Frontend: ${BLUE}$FRONTEND_URL${NC}"
echo ""
echo "Alternative access methods:"
echo "  Port forward frontend: kubectl port-forward svc/$FRONTEND_RELEASE 3000:80 -n $NAMESPACE"
echo "  Port forward backend:  kubectl port-forward svc/$BACKEND_RELEASE 8000:8000 -n $NAMESPACE"
echo ""
echo "Useful commands:"
echo "  View logs (backend):  kubectl logs -f -l app=todo-backend -n $NAMESPACE"
echo "  View logs (frontend): kubectl logs -f -l app=todo-frontend -n $NAMESPACE"
echo "  Delete deployment:    ./scripts/cleanup.sh"
echo ""

# Open browser automatically (optional)
read -p "Open frontend in browser? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    minikube service "$FRONTEND_RELEASE" -n "$NAMESPACE"
fi

# =============================================================================
# kubectl-ai Alternative Commands:
# =============================================================================
# If you have kubectl-ai installed, you can use these commands:
#
# Generate deployment:
#   kubectl-ai "Create a deployment for todo-backend with health checks"
#
# Scale deployment:
#   kubectl-ai "Scale todo-backend to 2 replicas in namespace todo-app"
#
# Debug pods:
#   kubectl-ai "Why is my todo-backend pod in CrashLoopBackOff?"
#
# Check resources:
#   kubectl-ai "Show resource usage for all pods in todo-app namespace"
# =============================================================================
