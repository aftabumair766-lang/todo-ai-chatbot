#!/bin/bash
# Build Docker images for all microservices
# Run this script after installing Docker and Minikube

set -e

echo "🐳 Building Docker images for Todo Chatbot microservices..."

# Build API Gateway
echo "📦 Building API Gateway..."
docker build -t todo-api-gateway:v1 services/api-gateway

# Build Task Service
echo "📦 Building Task Service..."
docker build -t todo-task-service:v1 services/task-service

# Build Scheduler Service
echo "📦 Building Scheduler Service..."
docker build -t todo-scheduler-service:v1 services/scheduler-service

# Build Notification Service
echo "📦 Building Notification Service..."
docker build -t todo-notification-service:v1 services/notification-service

echo "✅ All Docker images built successfully!"

# List images
echo ""
echo "📋 Built images:"
docker images | grep "todo-"

echo ""
echo "📝 Next step: Load images into Minikube"
echo "   Run: ./load-images-minikube.sh"
