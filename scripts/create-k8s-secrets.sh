#!/bin/bash
# =============================================================================
# Create Kubernetes Secrets from .env file
# =============================================================================
# This script reads secrets from .env and creates Kubernetes secrets
# WITHOUT exposing them in logs or terminal output
# =============================================================================

set -e

echo "🔐 Creating Kubernetes Secrets from .env file..."
echo ""

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
    echo "❌ Error: backend/.env file not found!"
    exit 1
fi

# Load environment variables from .env
export $(cat backend/.env | grep -v '^#' | grep -v '^$' | xargs)

# Check if namespace exists
if ! kubectl get namespace todo-app &> /dev/null; then
    echo "Creating namespace todo-app..."
    kubectl create namespace todo-app
fi

# Delete existing secret if it exists (to update)
kubectl delete secret todo-backend-secrets -n todo-app --ignore-not-found=true

# Create Kubernetes secret
echo "📝 Creating Kubernetes secret: todo-backend-secrets"
kubectl create secret generic todo-backend-secrets \
  -n todo-app \
  --from-literal=DATABASE_URL="$DATABASE_URL" \
  --from-literal=OPENAI_API_KEY="$OPENAI_API_KEY" \
  --from-literal=CHATKIT_WORKFLOW_ID="$CHATKIT_WORKFLOW_ID" \
  --from-literal=BETTER_AUTH_SECRET="$BETTER_AUTH_SECRET" \
  --from-literal=BETTER_AUTH_ISSUER="$BETTER_AUTH_ISSUER" \
  --from-literal=REDIS_URL="$REDIS_URL" \
  --from-literal=ENVIRONMENT="$ENVIRONMENT" \
  --from-literal=LOG_LEVEL="$LOG_LEVEL" \
  --from-literal=CORS_ORIGINS="$CORS_ORIGINS" \
  --from-literal=RATE_LIMIT_PER_MINUTE="$RATE_LIMIT_PER_MINUTE"

echo "✅ Secret created successfully!"
echo ""

# Verify secret was created
echo "🔍 Verifying secret..."
kubectl get secret todo-backend-secrets -n todo-app

echo ""
echo "📊 Secret contains these keys:"
kubectl get secret todo-backend-secrets -n todo-app -o jsonpath='{.data}' | jq -r 'keys[]'

echo ""
echo "✅ Done! Secrets are now available in Kubernetes"
echo ""
echo "💡 To use in deployment, reference them like:"
echo "   env:"
echo "     - name: OPENAI_API_KEY"
echo "       valueFrom:"
echo "         secretKeyRef:"
echo "           name: todo-backend-secrets"
echo "           key: OPENAI_API_KEY"
