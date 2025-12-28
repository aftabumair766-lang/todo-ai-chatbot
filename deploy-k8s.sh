#!/bin/bash
# Deploy Todo Chatbot to Kubernetes with Dapr
# This script handles T041 (Dapr components), T042 (secrets), and T043 (Helm deployment)

set -e

echo "☸️  Deploying Todo Chatbot to Kubernetes..."

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found. Please install kubectl first."
    exit 1
fi

# Check if Helm is available
if ! command -v helm &> /dev/null; then
    echo "❌ Helm not found. Please install Helm first."
    exit 1
fi

# Check if Minikube is running
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Kubernetes cluster not reachable. Please start Minikube:"
    echo "   minikube start --driver=docker --cpus=4 --memory=8192"
    exit 1
fi

# Create namespace
echo "📦 Creating namespace 'todo-app'..."
kubectl create namespace todo-app --dry-run=client -o yaml | kubectl apply -f -

# Deploy Kubernetes secrets (T042)
echo "🔐 Checking for Kubernetes secrets..."
if [ ! -f "kubernetes/base/secrets-local.yaml" ]; then
    echo "⚠️  Warning: kubernetes/base/secrets-local.yaml not found!"
    echo "   Please create this file with your actual credentials."
    echo "   Template available in kubernetes/base/secrets.yaml"
    echo ""
    read -p "Continue without secrets? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "🔐 Deploying Kubernetes secrets..."
    kubectl apply -f kubernetes/base/secrets-local.yaml -n todo-app
fi

# Deploy Dapr components (T041)
echo "🎯 Deploying Dapr components..."
kubectl apply -f kubernetes/dapr-components/ -n todo-app

# Wait for Dapr components to be ready
echo "⏳ Waiting for Dapr components to initialize..."
sleep 5

# Deploy with Helm (T043)
echo "📦 Deploying services with Helm..."
helm upgrade --install todo-app ./helm/todo-app \
    --namespace todo-app \
    --values ./helm/todo-app/values-dev.yaml \
    --create-namespace \
    --wait \
    --timeout 5m

echo "✅ Deployment complete!"

# Display pod status
echo ""
echo "📋 Pod Status:"
kubectl get pods -n todo-app

echo ""
echo "📋 Service Status:"
kubectl get svc -n todo-app

echo ""
echo "📋 Dapr Components:"
kubectl get components -n todo-app

echo ""
echo "📝 Next steps:"
echo "   1. Verify pods are running with Dapr sidecars:"
echo "      kubectl get pods -n todo-app"
echo "   2. Check Dapr sidecar logs:"
echo "      kubectl logs -n todo-app <pod-name> daprd"
echo "   3. Test API Gateway:"
echo "      kubectl port-forward -n todo-app svc/api-gateway 8000:8000"
echo "      curl http://localhost:8000/health"
