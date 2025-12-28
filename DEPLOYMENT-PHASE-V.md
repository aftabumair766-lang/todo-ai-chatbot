# Phase V Deployment Guide - Cloud-Native Microservices

Complete guide for deploying the cloud-native Todo Chatbot with Kubernetes, Dapr, and Kafka.

## Prerequisites (Manual Setup Required)

### 1. Install Docker Desktop
- Download from: https://www.docker.com/products/docker-desktop/
- Required for building images and running Minikube

### 2. Install Minikube + Dapr (T016)
```bash
# Install Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# Start Minikube with recommended resources
minikube start --driver=docker --cpus=4 --memory=8192

# Install Dapr CLI
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Initialize Dapr on Kubernetes
dapr init --kubernetes --wait

# Verify Dapr installation
dapr status -k
kubectl get pods -n dapr-system
```

### 3. Provision Redpanda Cloud Kafka (T009)
```bash
# Sign up at: https://redpanda.com/try-redpanda
# Create a free cluster (takes ~5 minutes)
# Note down:
#   - Bootstrap servers
#   - SASL username
#   - SASL password
```

### 4. Get SendGrid API Key
```bash
# Sign up at: https://sendgrid.com/
# Navigate to Settings > API Keys
# Create new API key with "Mail Send" permissions
# Note down the API key (starts with SG.)
```

### 5. Create Kubernetes Secrets (T042)
```bash
# Copy the secrets template
cp kubernetes/base/secrets.yaml kubernetes/base/secrets-local.yaml

# Edit with your actual credentials
nano kubernetes/base/secrets-local.yaml

# Replace placeholders:
#   - DATABASE_URL: Your Neon PostgreSQL URL
#   - KAFKA_BOOTSTRAP_SERVERS: Redpanda bootstrap servers
#   - KAFKA_SASL_USERNAME: Redpanda username
#   - KAFKA_SASL_PASSWORD: Redpanda password
#   - SENDGRID_API_KEY: Your SendGrid API key
#   - OPENAI_API_KEY: Your OpenAI API key
#   - BETTER_AUTH_SECRET: Generate with: openssl rand -hex 32
```

## Deployment Steps

### Phase 1: Build and Load Images

#### T039: Build Docker Images
```bash
# Build all service images
./build-images.sh

# Verify images
docker images | grep todo-
```

#### T040: Load Images into Minikube
```bash
# Load images into Minikube registry
./load-images-minikube.sh

# Verify images in Minikube
minikube image ls | grep todo-
```

### Phase 2: Deploy to Kubernetes

#### T041-T043: Deploy Everything
```bash
# Single command to deploy components, secrets, and services
./deploy-k8s.sh

# This script:
#   - Creates 'todo-app' namespace
#   - Deploys Kubernetes secrets (T042)
#   - Deploys Dapr components (T041)
#   - Deploys services with Helm (T043)
```

#### Manual Deployment (if needed)
```bash
# Create namespace
kubectl create namespace todo-app

# Deploy secrets
kubectl apply -f kubernetes/base/secrets-local.yaml -n todo-app

# Deploy Dapr components
kubectl apply -f kubernetes/dapr-components/ -n todo-app

# Deploy with Helm
helm upgrade --install todo-app ./helm/todo-app \
    --namespace todo-app \
    --values ./helm/todo-app/values-dev.yaml \
    --wait
```

### Phase 3: Verify and Test

#### T044: Verify Pods with Dapr Sidecars
```bash
# Check pod status (should see 2/2 containers per pod)
kubectl get pods -n todo-app

# Verify Dapr sidecars
kubectl get pods -n todo-app -o custom-columns='NAME:.metadata.name,CONTAINERS:.spec.containers[*].name'

# Check Dapr components
kubectl get components -n todo-app
```

#### T045: Test API Gateway Health
```bash
# Port-forward to API Gateway
kubectl port-forward -n todo-app svc/api-gateway 8000:8000

# Test health endpoint (in another terminal)
curl http://localhost:8000/health | jq '.'
```

#### T046: Test Task Creation and Kafka Events
```bash
# Create a test task
curl -X POST http://localhost:8000/tasks \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer test-token" \
    -d '{
        "title": "Test Task",
        "user_id": "test-user-123"
    }' | jq '.'

# Check Task Service logs for event publishing
kubectl logs -n todo-app -l app=task-service -c task-service --tail=50

# Check Dapr sidecar logs for Kafka events
kubectl logs -n todo-app -l app=task-service -c daprd --tail=50
```

#### Automated Testing
```bash
# Run all tests (T044-T046)
./test-deployment.sh
```

#### T047: Test Pod Restart and Recovery
```bash
# Delete a pod to test auto-recovery
kubectl delete pod -n todo-app -l app=task-service

# Watch pod restart
kubectl get pods -n todo-app -w

# Verify health after restart
kubectl logs -n todo-app -l app=task-service -c task-service --tail=20
```

## Troubleshooting

### Pods Not Starting
```bash
# Check pod events
kubectl describe pod -n todo-app <pod-name>

# Check container logs
kubectl logs -n todo-app <pod-name> -c <container-name>

# Check Dapr sidecar logs
kubectl logs -n todo-app <pod-name> -c daprd
```

### Dapr Components Not Working
```bash
# Verify components are registered
kubectl get components -n todo-app

# Check Dapr operator logs
kubectl logs -n dapr-system -l app=dapr-operator
```

### Secrets Not Loading
```bash
# Verify secret exists
kubectl get secret todo-secrets -n todo-app

# Check secret data
kubectl describe secret todo-secrets -n todo-app

# Verify pods can access secrets
kubectl exec -n todo-app <pod-name> -c <container-name> -- env | grep KAFKA
```

### Kafka Events Not Publishing
```bash
# Check Dapr sidecar logs for Kafka errors
kubectl logs -n todo-app -l app=task-service -c daprd | grep -i kafka

# Verify Pub/Sub component
kubectl describe component pubsub -n todo-app

# Test Kafka connectivity from pod
kubectl exec -n todo-app <pod-name> -c daprd -- wget -O- http://localhost:3500/v1.0/healthz
```

## Next Steps

### T048: Deploy to Cloud Kubernetes
Once local testing is complete, deploy to a cloud provider:

#### Option 1: AWS EKS
```bash
# Install eksctl
curl --silent --location "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin

# Create EKS cluster
eksctl create cluster \
    --name todo-chatbot \
    --region us-east-1 \
    --nodegroup-name standard-workers \
    --node-type t3.medium \
    --nodes 3

# Install Dapr
dapr init --kubernetes --wait

# Deploy (same as local)
./deploy-k8s.sh
```

#### Option 2: Google GKE
```bash
# Create GKE cluster
gcloud container clusters create todo-chatbot \
    --num-nodes=3 \
    --machine-type=e2-medium \
    --zone=us-central1-a

# Get credentials
gcloud container clusters get-credentials todo-chatbot --zone=us-central1-a

# Install Dapr
dapr init --kubernetes --wait

# Deploy
./deploy-k8s.sh
```

#### Option 3: Azure AKS
```bash
# Create AKS cluster
az aks create \
    --resource-group todo-chatbot-rg \
    --name todo-chatbot \
    --node-count 3 \
    --node-vm-size Standard_B2s

# Get credentials
az aks get-credentials --resource-group todo-chatbot-rg --name todo-chatbot

# Install Dapr
dapr init --kubernetes --wait

# Deploy
./deploy-k8s.sh
```

## Progress Tracking

- [x] T032: Create API Gateway FastAPI app
- [x] T033: Implement JWT auth middleware
- [x] T034: Create Task Service FastAPI app
- [x] T035: Implement task CRUD endpoints
- [x] T036: Implement Kafka event publisher
- [x] T037: Create Scheduler Service
- [x] T038: Create Notification Service
- [ ] T039: Build Docker images (manual: run `./build-images.sh`)
- [ ] T040: Load images into Minikube (manual: run `./load-images-minikube.sh`)
- [ ] T041: Deploy Dapr components (manual: run `./deploy-k8s.sh`)
- [ ] T042: Create Kubernetes secrets (manual: edit `kubernetes/base/secrets-local.yaml`)
- [ ] T043: Deploy with Helm (manual: run `./deploy-k8s.sh`)
- [ ] T044: Verify pods with Dapr sidecars (manual: run `./test-deployment.sh`)
- [ ] T045: Test API Gateway health (manual: run `./test-deployment.sh`)
- [ ] T046: Test task creation and Kafka events (manual: run `./test-deployment.sh`)
- [ ] T047: Test pod restart and recovery (manual)
- [ ] T048: Deploy to cloud Kubernetes (manual)

**Current Progress: 38/113 tasks (34%)**
