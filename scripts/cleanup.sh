#!/bin/bash
# =============================================================================
# Cleanup Script
# =============================================================================
# Purpose: Remove all Kubernetes resources deployed by Helm
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

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}Todo AI Chatbot - Cleanup Deployment${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Confirm cleanup
echo -e "${YELLOW}This will delete all Todo AI Chatbot resources from Minikube.${NC}"
read -p "Are you sure? (yes/no) " -r
echo

if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Cleanup cancelled."
    exit 0
fi

# -----------------------------------------------------------------------------
# Step 1: Uninstall Helm Releases
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[1/3] Uninstalling Helm releases...${NC}"

if helm list -n "$NAMESPACE" | grep -q "$FRONTEND_RELEASE"; then
    helm uninstall "$FRONTEND_RELEASE" -n "$NAMESPACE"
    echo -e "${GREEN}✓ Frontend release uninstalled${NC}"
else
    echo "Frontend release not found, skipping..."
fi

if helm list -n "$NAMESPACE" | grep -q "$BACKEND_RELEASE"; then
    helm uninstall "$BACKEND_RELEASE" -n "$NAMESPACE"
    echo -e "${GREEN}✓ Backend release uninstalled${NC}"
else
    echo "Backend release not found, skipping..."
fi

echo ""

# -----------------------------------------------------------------------------
# Step 2: Delete Secrets
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[2/3] Deleting secrets...${NC}"

kubectl delete secret "$BACKEND_RELEASE-secrets" -n "$NAMESPACE" --ignore-not-found=true
echo -e "${GREEN}✓ Secrets deleted${NC}"
echo ""

# -----------------------------------------------------------------------------
# Step 3: Delete Namespace
# -----------------------------------------------------------------------------
echo -e "${YELLOW}[3/3] Deleting namespace...${NC}"

kubectl delete namespace "$NAMESPACE" --ignore-not-found=true
echo -e "${GREEN}✓ Namespace deleted${NC}"
echo ""

# -----------------------------------------------------------------------------
# Step 4: Verify Cleanup
# -----------------------------------------------------------------------------
echo -e "${YELLOW}Verifying cleanup...${NC}"

if kubectl get namespace "$NAMESPACE" &> /dev/null; then
    echo -e "${YELLOW}Namespace is being deleted (may take a few moments)...${NC}"
else
    echo -e "${GREEN}✓ All resources cleaned up${NC}"
fi

echo ""

# -----------------------------------------------------------------------------
# Summary
# -----------------------------------------------------------------------------
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}Cleanup Complete!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "All Todo AI Chatbot resources have been removed from Minikube."
echo ""
echo "To redeploy:"
echo "  ./scripts/deploy-minikube.sh"
echo ""
echo "To stop Minikube:"
echo "  minikube stop"
echo ""
echo "To delete Minikube cluster:"
echo "  minikube delete"
echo ""
