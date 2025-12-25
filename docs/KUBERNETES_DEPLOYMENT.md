# Kubernetes Deployment Guide - Todo AI Chatbot

**Phase IV: Cloud-Native Deployment with AI-Assisted DevOps**

This guide walks you through deploying the Todo AI Chatbot on a local Kubernetes cluster using Minikube and Helm, while demonstrating AI-assisted DevOps practices.

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Architecture](#architecture)
4. [Installation](#installation)
5. [Deployment Steps](#deployment-steps)
6. [Accessing the Application](#accessing-the-application)
7. [Monitoring & Debugging](#monitoring--debugging)
8. [Scaling](#scaling)
9. [Troubleshooting](#troubleshooting)
10. [Cleanup](#cleanup)

---

## Overview

### What You're Building

You're deploying a **cloud-native microservices architecture** locally on Kubernetes:

- **Backend**: FastAPI with OpenAI GPT-4 integration (containerized)
- **Frontend**: React + TypeScript served by Nginx (containerized)
- **Database**: External Neon PostgreSQL (managed cloud database)
- **Orchestration**: Kubernetes via Minikube
- **Package Management**: Helm charts for reusable deployments

### Why This Approach?

| Benefit | Description |
|---------|-------------|
| **Portability** | Runs the same in dev, staging, and production |
| **Scalability** | Easy to scale with replica sets |
| **Reliability** | Self-healing, automatic restarts, health checks |
| **Declarative** | Infrastructure as Code (IaC) via Helm charts |
| **Production-Ready** | Same patterns used in real-world cloud deployments |

---

## Prerequisites

### Required Software

#### 1. Docker Desktop

**Why**: Build container images

**Install**:
```bash
# macOS
brew install --cask docker

# Windows
# Download from: https://www.docker.com/products/docker-desktop

# Linux
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
```

**Verify**:
```bash
docker --version
# Output: Docker version 24.0.0+
```

---

#### 2. Minikube

**Why**: Local Kubernetes cluster

**Install**:
```bash
# macOS
brew install minikube

# Windows (PowerShell as Admin)
choco install minikube

# Linux
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

**Verify**:
```bash
minikube version
# Output: minikube version: v1.32.0
```

---

#### 3. kubectl

**Why**: Kubernetes command-line tool

**Install**:
```bash
# macOS
brew install kubectl

# Windows
choco install kubernetes-cli

# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
```

**Verify**:
```bash
kubectl version --client
# Output: Client Version: v1.29.0
```

---

#### 4. Helm

**Why**: Kubernetes package manager (like npm for K8s)

**Install**:
```bash
# macOS
brew install helm

# Windows
choco install kubernetes-helm

# Linux
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

**Verify**:
```bash
helm version
# Output: version.BuildInfo{Version:"v3.13.0"...}
```

---

#### 5. Docker AI (Gordon) - Optional

**Why**: AI-assisted Dockerfile generation and optimization

**Install**:
```bash
# Requires Docker Desktop with AI features enabled
# Enable in Docker Desktop settings: Features → Beta Features → Docker AI
```

**Verify**:
```bash
docker ai "Hello, are you working?"
# Should respond with AI-generated response
```

---

#### 6. kubectl-ai - Optional

**Why**: AI-assisted Kubernetes manifest generation

**Install**:
```bash
# Install via npm
npm install -g kubectl-ai

# Or via pip
pip install kubectl-ai
```

**Verify**:
```bash
kubectl-ai --version
# Output: kubectl-ai version 1.0.0
```

---

### System Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 2 cores | 4 cores |
| RAM | 4 GB | 8 GB |
| Disk | 20 GB free | 40 GB free |
| OS | macOS 10.13+, Windows 10+, Linux | Latest |

---

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Minikube Cluster                        │
│                                                             │
│  ┌──────────────────────┐      ┌──────────────────────┐   │
│  │   Frontend Pod       │      │   Backend Pod        │   │
│  │  ┌───────────────┐   │      │  ┌───────────────┐   │   │
│  │  │  Nginx:Alpine │   │      │  │  FastAPI      │   │   │
│  │  │  (Static SPA) │   │      │  │  + OpenAI SDK │   │   │
│  │  │   Port 80     │───┼──────┼─▶│   Port 8000   │   │   │
│  │  └───────────────┘   │      │  └───────────────┘   │   │
│  │  Replicas: 1         │      │  Replicas: 1         │   │
│  └──────────────────────┘      └──────────────────────┘   │
│           │                              │                 │
│      NodePort (30080)            ClusterIP (8000)         │
│           │                              │                 │
└───────────┼──────────────────────────────┼─────────────────┘
            │                              │
       [User Browser]               [Neon PostgreSQL]
   http://localhost:30080           (External Cloud DB)
```

### Component Breakdown

| Component | Technology | Purpose | Port |
|-----------|-----------|---------|------|
| **Frontend** | React 18 + TypeScript + Nginx | User interface | 80 → 30080 (NodePort) |
| **Backend** | FastAPI + Python 3.11 | REST API + AI logic | 8000 (ClusterIP) |
| **Database** | Neon PostgreSQL | Data persistence | 5432 (External) |
| **Orchestrator** | Kubernetes (Minikube) | Container management | - |
| **Package Manager** | Helm | Deployment automation | - |

---

## Installation

### Step 1: Start Minikube

Start a local Kubernetes cluster with appropriate resources:

```bash
# Start Minikube with 2 CPUs and 4GB RAM (minimal config)
minikube start --cpus=2 --memory=4096 --driver=docker

# For better performance (if you have resources):
# minikube start --cpus=4 --memory=8192 --driver=docker
```

**Expected Output**:
```
😄  minikube v1.32.0 on Darwin 14.1.1
✨  Using the docker driver based on user configuration
👍  Starting control plane node minikube in cluster minikube
🔥  Creating docker container (CPUs=2, Memory=4096MB) ...
🐳  Preparing Kubernetes v1.28.3 on Docker 24.0.7 ...
🔗  Configuring bridge CNI (Container Networking Interface) ...
🔎  Verifying Kubernetes components...
🌟  Enabled addons: storage-provisioner, default-storageclass
🏄  Done! kubectl is now configured to use "minikube" cluster
```

**Verify**:
```bash
minikube status
```

Output:
```
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured
```

---

### Step 2: Verify kubectl Configuration

```bash
kubectl cluster-info
```

**Expected Output**:
```
Kubernetes control plane is running at https://192.168.49.2:8443
CoreDNS is running at https://192.168.49.2:8443/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy
```

---

### Step 3: Prepare Environment Variables

Create a `.env` file in the `backend/` directory with your secrets:

```bash
cd /home/umair/todo-chatbot/backend
cp .env.example .env
```

Edit `.env` and add your actual values:

```bash
# Required
DATABASE_URL=postgresql+asyncpg://user:password@your-neon-host.neon.tech/dbname?ssl=require
OPENAI_API_KEY=sk-proj-your-actual-api-key-here

# Optional
BETTER_AUTH_SECRET=your-32-character-random-secret-key
BETTER_AUTH_ISSUER=http://localhost:8000
ENVIRONMENT=production
LOG_LEVEL=INFO
```

⚠️ **IMPORTANT**: Never commit `.env` to Git (already in `.gitignore`)

---

## Deployment Steps

### Quick Deployment (3 Commands)

```bash
# 1. Build Docker images and load into Minikube
./scripts/build-images.sh

# 2. Deploy to Kubernetes
./scripts/deploy-minikube.sh

# 3. Access the application
# URL will be displayed at the end of deployment
```

---

### Manual Deployment (Step-by-Step)

If you want to understand each step:

#### Step 1: Build Backend Image

```bash
cd /home/umair/todo-chatbot/backend
docker build -t todo-backend:v1 .
```

**Docker AI Alternative**:
```bash
docker ai "Build this Dockerfile and tag it as todo-backend:v1"
```

**Expected Output**:
```
[+] Building 45.2s (12/12) FINISHED
=> [internal] load build definition
=> => transferring dockerfile
=> [internal] load .dockerignore
=> [stage-0 1/4] FROM docker.io/library/python:3.11-slim
...
=> => naming to docker.io/library/todo-backend:v1
```

---

#### Step 2: Build Frontend Image

```bash
cd /home/umair/todo-chatbot/frontend
docker build -t todo-frontend:v1 .
```

**Expected Output**:
```
[+] Building 120.5s (15/15) FINISHED
=> [builder 1/6] FROM docker.io/library/node:18
=> [builder 2/6] COPY package*.json ./
=> [builder 3/6] RUN npm ci
=> [builder 4/6] COPY . .
=> [builder 5/6] RUN npm run build
=> [stage-1 1/3] FROM docker.io/library/nginx:alpine
=> [stage-1 2/3] COPY --from=builder /app/dist /usr/share/nginx/html
=> => naming to docker.io/library/todo-frontend:v1
```

---

#### Step 3: Load Images into Minikube

```bash
minikube image load todo-backend:v1
minikube image load todo-frontend:v1
```

**Verify Images**:
```bash
minikube image ls | grep todo
```

Output:
```
docker.io/library/todo-backend:v1
docker.io/library/todo-frontend:v1
```

---

#### Step 4: Create Kubernetes Namespace

```bash
kubectl create namespace todo-app
```

**Verify**:
```bash
kubectl get namespaces
```

---

#### Step 5: Create Secrets

```bash
cd /home/umair/todo-chatbot

# Load environment variables
source backend/.env

# Create secret
kubectl create secret generic todo-backend-secrets \
  --from-literal=openai-api-key="$OPENAI_API_KEY" \
  --from-literal=database-url="$DATABASE_URL" \
  --from-literal=better-auth-secret="$BETTER_AUTH_SECRET" \
  --from-literal=better-auth-issuer="$BETTER_AUTH_ISSUER" \
  --namespace=todo-app
```

**Verify Secret**:
```bash
kubectl get secrets -n todo-app
```

Output:
```
NAME                    TYPE     DATA   AGE
todo-backend-secrets    Opaque   4      10s
```

---

#### Step 6: Deploy Backend with Helm

```bash
helm install todo-backend ./helm/todo-backend \
  --namespace=todo-app \
  --set image.pullPolicy=Never \
  --wait
```

**Expected Output**:
```
NAME: todo-backend
LAST DEPLOYED: Thu Dec 19 10:30:00 2025
NAMESPACE: todo-app
STATUS: deployed
REVISION: 1
```

**Verify Deployment**:
```bash
kubectl get pods -n todo-app
```

Output:
```
NAME                            READY   STATUS    RESTARTS   AGE
todo-backend-7d9f8c4b6d-xk2lp   1/1     Running   0          30s
```

---

#### Step 7: Deploy Frontend with Helm

```bash
helm install todo-frontend ./helm/todo-frontend \
  --namespace=todo-app \
  --set image.pullPolicy=Never \
  --set env.VITE_API_URL="http://todo-backend:8000" \
  --wait
```

**Verify Deployment**:
```bash
kubectl get pods -n todo-app
```

Output:
```
NAME                             READY   STATUS    RESTARTS   AGE
todo-backend-7d9f8c4b6d-xk2lp    1/1     Running   0          2m
todo-frontend-6c8b9d4f7e-zn3km   1/1     Running   0          15s
```

---

#### Step 8: Verify Services

```bash
kubectl get svc -n todo-app
```

**Expected Output**:
```
NAME            TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
todo-backend    ClusterIP   10.96.100.200   <none>        8000/TCP       2m
todo-frontend   NodePort    10.96.150.100   <none>        80:30080/TCP   1m
```

---

## Accessing the Application

### Method 1: Minikube Service (Recommended)

```bash
minikube service todo-frontend -n todo-app
```

This automatically opens your browser to the frontend URL.

**Manual URL**:
```bash
minikube service todo-frontend -n todo-app --url
```

Example output: `http://192.168.49.2:30080`

---

### Method 2: Port Forwarding

Forward the frontend service to localhost:

```bash
kubectl port-forward svc/todo-frontend 3000:80 -n todo-app
```

Access at: http://localhost:3000

**Backend API (for testing)**:
```bash
kubectl port-forward svc/todo-backend 8000:8000 -n todo-app
```

Access API docs at: http://localhost:8000/docs

---

### Method 3: NodePort (Direct)

If you know your Minikube IP:

```bash
# Get Minikube IP
minikube ip
```

Output example: `192.168.49.2`

Access: `http://192.168.49.2:30080`

---

## Monitoring & Debugging

### View Logs

**Backend logs**:
```bash
kubectl logs -f -l app=todo-backend -n todo-app
```

**Frontend logs**:
```bash
kubectl logs -f -l app=todo-frontend -n todo-app
```

**Specific pod**:
```bash
# List pods
kubectl get pods -n todo-app

# View logs
kubectl logs <pod-name> -n todo-app
```

---

### Check Pod Health

```bash
kubectl get pods -n todo-app -o wide
```

**Detailed pod info**:
```bash
kubectl describe pod <pod-name> -n todo-app
```

---

### Execute Commands in Pod

**Open shell in backend pod**:
```bash
kubectl exec -it <backend-pod-name> -n todo-app -- /bin/bash
```

**Run a command**:
```bash
kubectl exec <backend-pod-name> -n todo-app -- python -c "import sys; print(sys.version)"
```

---

### Health Check Status

**Backend health check**:
```bash
kubectl port-forward svc/todo-backend 8000:8000 -n todo-app &
curl http://localhost:8000/health
```

Output:
```json
{
  "status": "healthy",
  "service": "todo-ai-chatbot",
  "version": "1.0.0",
  "environment": "production"
}
```

---

### Resource Usage

**Pod resource usage**:
```bash
kubectl top pods -n todo-app
```

Output:
```
NAME                             CPU(cores)   MEMORY(bytes)
todo-backend-7d9f8c4b6d-xk2lp    50m          200Mi
todo-frontend-6c8b9d4f7e-zn3km   10m          50Mi
```

**Node resource usage**:
```bash
kubectl top nodes
```

---

### Using kubectl-ai for Debugging

**Why is my pod failing?**
```bash
kubectl-ai "Why is my todo-backend pod in CrashLoopBackOff state?"
```

**Check resource usage**:
```bash
kubectl-ai "Show me resource usage for all pods in todo-app namespace"
```

**Generate debugging commands**:
```bash
kubectl-ai "How do I debug a pod that's not starting in Kubernetes?"
```

---

## Scaling

### Manual Scaling

**Scale backend to 2 replicas**:
```bash
kubectl scale deployment/todo-backend --replicas=2 -n todo-app
```

**Verify**:
```bash
kubectl get pods -n todo-app
```

Output:
```
NAME                             READY   STATUS    RESTARTS   AGE
todo-backend-7d9f8c4b6d-xk2lp    1/1     Running   0          5m
todo-backend-7d9f8c4b6d-abc12    1/1     Running   0          10s
todo-frontend-6c8b9d4f7e-zn3km   1/1     Running   0          5m
```

---

### Scale with Helm

Update `helm/todo-backend/values.yaml`:

```yaml
replicaCount: 2
```

Apply changes:
```bash
helm upgrade todo-backend ./helm/todo-backend -n todo-app
```

---

### kubectl-ai Scaling

```bash
kubectl-ai "Scale todo-backend deployment to 3 replicas in namespace todo-app"
```

---

### Auto-scaling (Optional)

Enable autoscaling in `values.yaml`:

```yaml
autoscaling:
  enabled: true
  minReplicas: 1
  maxReplicas: 5
  targetCPUUtilizationPercentage: 80
```

Deploy:
```bash
helm upgrade todo-backend ./helm/todo-backend -n todo-app
```

---

## Troubleshooting

### Pod Not Starting

**Symptoms**: Pod stuck in `ContainerCreating` or `CrashLoopBackOff`

**Debug**:
```bash
# Check pod events
kubectl describe pod <pod-name> -n todo-app

# Check logs
kubectl logs <pod-name> -n todo-app

# Check previous container logs (if restarting)
kubectl logs <pod-name> -n todo-app --previous
```

**Common Causes**:
- Missing secrets → Check: `kubectl get secrets -n todo-app`
- Image not found → Check: `minikube image ls | grep todo`
- Invalid environment variables → Check deployment YAML

---

### Service Not Accessible

**Symptoms**: Cannot access frontend via browser

**Debug**:
```bash
# Check service
kubectl get svc -n todo-app

# Check endpoints
kubectl get endpoints -n todo-app

# Verify pods are running
kubectl get pods -n todo-app
```

**Common Causes**:
- Pods not ready → Check health probes
- Wrong NodePort → Verify service configuration
- Minikube tunnel needed → Run: `minikube tunnel`

---

### Backend Can't Connect to Database

**Symptoms**: Backend pod restarts repeatedly

**Debug**:
```bash
# Check backend logs
kubectl logs -f -l app=todo-backend -n todo-app

# Verify secrets
kubectl get secret todo-backend-secrets -n todo-app -o yaml
```

**Common Causes**:
- Wrong `DATABASE_URL` in secret
- Neon database not accessible from Minikube
- Missing SSL parameters in connection string

**Fix**:
```bash
# Delete old secret
kubectl delete secret todo-backend-secrets -n todo-app

# Recreate with correct values
kubectl create secret generic todo-backend-secrets \
  --from-literal=database-url="postgresql+asyncpg://...?ssl=require" \
  --namespace=todo-app

# Restart backend pods
kubectl rollout restart deployment/todo-backend -n todo-app
```

---

### Image Pull Errors

**Symptoms**: `ImagePullBackOff` or `ErrImagePull`

**Debug**:
```bash
kubectl describe pod <pod-name> -n todo-app
```

**Common Causes**:
- Image not loaded into Minikube
- Wrong image name/tag

**Fix**:
```bash
# Rebuild and load images
./scripts/build-images.sh

# Or manually:
minikube image load todo-backend:v1
minikube image load todo-frontend:v1

# Restart deployment
kubectl rollout restart deployment/todo-backend -n todo-app
kubectl rollout restart deployment/todo-frontend -n todo-app
```

---

### Health Check Failures

**Symptoms**: Pods keep restarting

**Debug**:
```bash
kubectl describe pod <pod-name> -n todo-app
# Look for: Liveness probe failed, Readiness probe failed
```

**Common Causes**:
- Health check endpoint not responding
- Initial delay too short

**Temporary Fix** (disable health checks):
```bash
# Edit deployment
kubectl edit deployment/todo-backend -n todo-app

# Comment out livenessProbe and readinessProbe sections
# Save and exit
```

---

## Cleanup

### Remove Deployment

**Using script**:
```bash
./scripts/cleanup.sh
```

**Manual cleanup**:
```bash
# Uninstall Helm releases
helm uninstall todo-backend -n todo-app
helm uninstall todo-frontend -n todo-app

# Delete secrets
kubectl delete secret todo-backend-secrets -n todo-app

# Delete namespace
kubectl delete namespace todo-app
```

---

### Stop Minikube

```bash
minikube stop
```

---

### Delete Minikube Cluster

```bash
minikube delete
```

⚠️ **Warning**: This deletes all data in the Minikube cluster

---

## Next Steps

1. **Explore Helm Charts**: Review `helm/todo-backend/` and `helm/todo-frontend/`
2. **Read AI DevOps Guide**: See `docs/AI_DEVOPS_GUIDE.md` for AI tool examples
3. **Study Research**: Read `docs/PHASE_IV_RESEARCH.md` for spec-driven infrastructure concepts
4. **Try kubectl-ai**: Experiment with AI-assisted Kubernetes operations
5. **Customize**: Modify Helm `values.yaml` files to change resources, replicas, etc.

---

## Additional Resources

- **Kubernetes Documentation**: https://kubernetes.io/docs/
- **Helm Documentation**: https://helm.sh/docs/
- **Minikube Documentation**: https://minikube.sigs.k8s.io/docs/
- **Docker Documentation**: https://docs.docker.com/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Project GitHub**: https://github.com/aftabumair766-lang/todo-ai-chatbot

---

**Last Updated**: December 19, 2025
**Author**: Umair
**Phase**: IV - Kubernetes Deployment
