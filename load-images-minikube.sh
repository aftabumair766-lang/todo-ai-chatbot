#!/bin/bash
# Load Docker images into Minikube
# Run this script after building images with build-images.sh

set -e

echo "🚀 Loading Docker images into Minikube..."

# Check if Minikube is running
if ! minikube status &> /dev/null; then
    echo "❌ Minikube is not running. Please start Minikube first:"
    echo "   minikube start --driver=docker --cpus=4 --memory=8192"
    exit 1
fi

# Load images into Minikube
echo "📦 Loading API Gateway image..."
minikube image load todo-api-gateway:v1

echo "📦 Loading Task Service image..."
minikube image load todo-task-service:v1

echo "📦 Loading Scheduler Service image..."
minikube image load todo-scheduler-service:v1

echo "📦 Loading Notification Service image..."
minikube image load todo-notification-service:v1

echo "✅ All images loaded into Minikube!"

# Verify images are loaded
echo ""
echo "📋 Images in Minikube:"
minikube image ls | grep "todo-"

echo ""
echo "📝 Next step: Deploy Dapr components to Kubernetes"
echo "   Run: kubectl apply -f kubernetes/dapr-components/"
