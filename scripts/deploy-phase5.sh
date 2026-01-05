#!/bin/bash
# =============================================================================
# Phase V Deployment Script - Deploy Event-Driven Architecture
# =============================================================================
# This script deploys Phase V after Redpanda credentials are obtained
# Usage: ./scripts/deploy-phase5.sh
# =============================================================================

set -e  # Exit on error

echo "🚀 Phase V Deployment - Event-Driven Architecture"
echo "=================================================="
echo ""

# Check if running from project root
if [ ! -f "PHASE_V_IMPLEMENTATION.md" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "   Example: ./scripts/deploy-phase5.sh"
    exit 1
fi

# Check if Minikube is running
echo "📋 Checking Minikube status..."
if ! minikube status &> /dev/null; then
    echo "❌ Minikube is not running. Starting Minikube..."
    minikube start --driver=docker
else
    echo "✅ Minikube is running"
fi

# Check if namespace exists
echo ""
echo "📋 Checking Kubernetes namespace..."
if ! kubectl get namespace todo-app &> /dev/null; then
    echo "Creating namespace todo-app..."
    kubectl create namespace todo-app
fi
echo "✅ Namespace todo-app exists"

# Check if Dapr is installed
echo ""
echo "📋 Checking Dapr installation..."
if ! dapr status -k &> /dev/null; then
    echo "❌ Dapr is not installed. Please install Dapr:"
    echo "   dapr init -k"
    exit 1
fi
echo "✅ Dapr is installed"

# Check if Kafka component file exists
echo ""
echo "📋 Checking Kafka component configuration..."
if [ ! -f "kubernetes/dapr-components/pubsub-kafka.yaml" ]; then
    echo "❌ Kafka component not configured!"
    echo ""
    echo "Please configure Kafka credentials first:"
    echo "1. Copy template:"
    echo "   cp kubernetes/dapr-components/pubsub-kafka.yaml.template \\"
    echo "      kubernetes/dapr-components/pubsub-kafka.yaml"
    echo ""
    echo "2. Edit the file and replace placeholders:"
    echo "   - YOUR_BOOTSTRAP_SERVER"
    echo "   - YOUR_SASL_USERNAME"
    echo "   - YOUR_SASL_PASSWORD"
    echo ""
    echo "3. Run this script again"
    exit 1
fi
echo "✅ Kafka component configuration found"

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
if [ -d "venv" ]; then
    source venv/bin/activate
    pip install -r backend/requirements.txt -q
    echo "✅ Dependencies installed"
else
    echo "⚠️  Virtual environment not found, skipping dependency install"
fi

# Build Docker image with Dapr SDK
echo ""
echo "🐳 Building Docker image with Phase V features..."
cd backend
docker build -t todo-backend:phase5 -f Dockerfile . -q
cd ..
echo "✅ Docker image built: todo-backend:phase5"

# Load image into Minikube
echo ""
echo "📥 Loading image into Minikube..."
minikube image load todo-backend:phase5
echo "✅ Image loaded into Minikube"

# Apply Kafka component
echo ""
echo "📡 Applying Kafka component to Kubernetes..."
kubectl apply -f kubernetes/dapr-components/pubsub-kafka.yaml -n todo-app
echo "✅ Kafka component applied"

# Verify component
echo ""
echo "🔍 Verifying Dapr component..."
kubectl get component -n todo-app
echo ""

# Update deployment with new image
echo "🔄 Updating backend deployment..."
if kubectl get deployment todo-backend -n todo-app &> /dev/null; then
    # Update existing deployment
    kubectl set image deployment/todo-backend backend=todo-backend:phase5 -n todo-app

    # Restart to pick up new annotations
    kubectl rollout restart deployment/todo-backend -n todo-app

    echo "⏳ Waiting for rollout to complete..."
    kubectl rollout status deployment/todo-backend -n todo-app --timeout=120s
else
    # Deploy using simple manifest
    kubectl apply -f k8s-simple-deploy.yaml

    # Update image
    kubectl set image deployment/todo-backend backend=todo-backend:phase5 -n todo-app

    echo "⏳ Waiting for deployment..."
    kubectl wait --for=condition=available deployment/todo-backend -n todo-app --timeout=120s
fi
echo "✅ Backend deployment updated"

# Check pod status
echo ""
echo "📊 Pod Status:"
kubectl get pods -n todo-app -l app=todo-backend
echo ""

# Verify Dapr sidecar
echo "🔍 Verifying Dapr sidecar injection..."
POD_NAME=$(kubectl get pods -n todo-app -l app=todo-backend -o jsonpath='{.items[0].metadata.name}')
CONTAINER_COUNT=$(kubectl get pod $POD_NAME -n todo-app -o jsonpath='{.spec.containers[*].name}' | wc -w)

if [ "$CONTAINER_COUNT" -eq "2" ]; then
    echo "✅ Dapr sidecar is injected (2/2 containers)"
else
    echo "⚠️  Warning: Expected 2 containers, found $CONTAINER_COUNT"
    echo "   Containers: $(kubectl get pod $POD_NAME -n todo-app -o jsonpath='{.spec.containers[*].name}')"
fi

# Show Dapr logs
echo ""
echo "📜 Recent Dapr sidecar logs:"
echo "----------------------------"
kubectl logs $POD_NAME -n todo-app -c daprd --tail=20 || echo "⚠️  Dapr container not ready yet"

# Deployment summary
echo ""
echo "=============================================="
echo "✅ Phase V Deployment Complete!"
echo "=============================================="
echo ""
echo "📊 Deployment Summary:"
echo "  - Namespace: todo-app"
echo "  - Image: todo-backend:phase5"
echo "  - Dapr Component: todo-pubsub"
echo "  - Pod: $POD_NAME"
echo ""
echo "🧪 Next Steps - Testing:"
echo "  1. Create a task (via UI or API)"
echo "  2. Check Dapr logs:"
echo "     kubectl logs $POD_NAME -n todo-app -c daprd -f"
echo "  3. Verify events in Redpanda Console:"
echo "     https://cloud.redpanda.com → Topics → task-events"
echo ""
echo "📚 Documentation:"
echo "  - Implementation Guide: PHASE_V_IMPLEMENTATION.md"
echo "  - Component Setup: kubernetes/dapr-components/README.md"
echo ""
echo "🎉 Event-driven architecture is now LIVE!"
