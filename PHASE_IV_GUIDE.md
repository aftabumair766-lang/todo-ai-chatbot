# Phase IV - Kubernetes Deployment Guide 🚀

## ✅ Current Status

### What's Already Done (70% Complete!):

✅ **Docker Setup:**
- Frontend Dockerfile (`frontend/Dockerfile`)
- Backend Dockerfile (`backend/Dockerfile`)
- docker-compose.yml
- .dockerignore files

✅ **Kubernetes Setup:**
- Helm charts (`helm/todo-app/`, `helm/todo-backend/`, `helm/todo-frontend/`)
- Base configurations (`kubernetes/base/`)
- Dapr components (`kubernetes/dapr-components/`)
- Deployment scripts

✅ **Tools:**
- Minikube v1.37.0 installed
- kubectl v1.34.3 installed
- Ready to deploy!

---

## 🎯 Phase IV Requirements

From Hackathon:
1. ✅ Containerize frontend and backend (DONE)
2. ⚠️ Use Docker AI Agent (Gordon) - Optional if not available
3. ✅ Create Helm charts (DONE)
4. ⚠️ Deploy on Minikube (IN PROGRESS)
5. ⚠️ Use kubectl-ai and kagent (TODO)

---

## 📦 What You Have

### 1. Frontend Dockerfile (`frontend/Dockerfile`)

```dockerfile
# Multi-stage build
FROM node:18 as builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
```

### 2. Backend Dockerfile (`backend/Dockerfile`)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 3. Helm Chart Structure

```
helm/todo-app/
├── Chart.yaml
├── values.yaml
├── values-dev.yaml
├── values-prod.yaml
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    ├── ingress.yaml
    └── configmap.yaml
```

---

## 🚀 Deployment Steps

### Step 1: Start Minikube ✅

```bash
# Start Minikube (DONE - running now)
minikube start --driver=docker

# Verify
minikube status
kubectl get nodes
```

### Step 2: Build Docker Images

```bash
cd /home/umair/todo-chatbot

# Build backend
docker build -t todo-backend:latest ./backend

# Build frontend
docker build -t todo-frontend:latest ./frontend

# Load images into Minikube
minikube image load todo-backend:latest
minikube image load todo-frontend:latest
```

### Step 3: Deploy with Helm

```bash
# Deploy the application
helm install todo-app ./helm/todo-app

# Check deployment
kubectl get pods
kubectl get services
```

### Step 4: Access the Application

```bash
# Get the service URL
minikube service todo-frontend --url

# Or use port forwarding
kubectl port-forward service/todo-frontend 3000:80
kubectl port-forward service/todo-backend 8000:8000
```

---

## 🤖 kubectl-ai Usage Examples

### Install kubectl-ai

```bash
# Install kubectl-ai
pip install kubectl-ai

# Configure
kubectl-ai config set-key YOUR_OPENAI_KEY
```

### Usage Examples for Phase IV

```bash
# Deploy the application
kubectl-ai "deploy todo app with 2 replicas"

# Check status
kubectl-ai "show me all pods and their status"

# Scale up
kubectl-ai "scale the backend to 3 replicas"

# Debug issues
kubectl-ai "why are my pods not running"

# Check logs
kubectl-ai "show logs for the backend pod"

# Update deployment
kubectl-ai "update frontend image to latest version"

# Check resources
kubectl-ai "show resource usage for all pods"
```

---

## 🔧 kagent Usage Examples

### Install kagent

```bash
# Install kagent
curl -fsSL https://raw.githubusercontent.com/k8scommunitylabs/k8s-agent/main/install.sh | bash
```

### Usage Examples

```bash
# Analyze cluster health
kagent "analyze the cluster health"

# Optimize resources
kagent "optimize resource allocation for my pods"

# Security check
kagent "check for security vulnerabilities"

# Performance analysis
kagent "analyze performance bottlenecks"

# Best practices
kagent "suggest improvements for my deployment"
```

---

## 📋 Testing Checklist

### Before Submission:

- [ ] Minikube running successfully
- [ ] Docker images built
- [ ] Images loaded into Minikube
- [ ] Helm deployment successful
- [ ] Frontend accessible
- [ ] Backend API responding
- [ ] Database connectivity working
- [ ] kubectl-ai commands documented
- [ ] kagent usage documented
- [ ] Screenshots taken
- [ ] Demo video recorded (90 seconds)

---

## 🎬 Demo Video Script (90 seconds)

**Seconds 0-15: Introduction**
"Hi! This is my Phase IV Kubernetes deployment for the Todo AI Chatbot. I've containerized both frontend and backend using Docker."

**Seconds 15-30: Show Dockerfiles**
"Here are my Dockerfiles for the React frontend and FastAPI backend. Both use multi-stage builds for optimization."

**Seconds 30-45: Show Minikube**
```bash
minikube status
kubectl get pods
kubectl get services
```
"The application is running on Minikube with 2 replicas each."

**Seconds 45-60: Show kubectl-ai**
```bash
kubectl-ai "show me all running pods"
kubectl-ai "check the health of my deployment"
```
"I'm using kubectl-ai for AI-assisted Kubernetes operations."

**Seconds 60-75: Show Application**
```bash
minikube service todo-frontend --url
```
"Here's the application running - you can see the chatbot interface working perfectly."

**Seconds 75-90: Helm Charts**
"All deployment is managed through Helm charts for easy versioning and rollback. Thank you!"

---

## 📁 Files to Submit

### GitHub Repository Structure:

```
todo-ai-chatbot/
├── README.md (updated with Phase IV section)
├── PHASE_IV_GUIDE.md (this file)
├── frontend/
│   ├── Dockerfile
│   ├── .dockerignore
│   └── nginx.conf
├── backend/
│   ├── Dockerfile
│   └── .dockerignore
├── docker-compose.yml
├── kubernetes/
│   ├── base/
│   └── dapr-components/
├── helm/
│   ├── todo-app/
│   ├── todo-backend/
│   └── todo-frontend/
└── docs/
    ├── kubectl-ai-examples.md
    └── kagent-usage.md
```

---

## 🎯 Submission Form

**Phase IV Submission:**

1. **GitHub Link:**
   ```
   https://github.com/aftabumair766-lang/todo-ai-chatbot
   Tag: phase-iv
   ```

2. **Demo Video:**
   - Duration: 90 seconds
   - Shows: Dockerfiles, Minikube, Helm, kubectl-ai, running app
   - Upload to: YouTube (unlisted) or Google Drive

3. **README Section:**
   - Add "Phase IV: Kubernetes Deployment" section
   - Include setup instructions
   - Document kubectl-ai usage
   - Screenshots of running pods

4. **Documentation:**
   - This guide (PHASE_IV_GUIDE.md)
   - kubectl-ai examples
   - kagent usage examples

---

## ⚠️ Common Issues & Solutions

### Issue 1: Minikube Won't Start
```bash
# Solution: Delete and restart
minikube delete
minikube start --driver=docker --memory=2048mb
```

### Issue 2: Images Not Found
```bash
# Solution: Load images into Minikube
eval $(minikube docker-env)
docker build -t todo-backend:latest ./backend
docker build -t todo-frontend:latest ./frontend
```

### Issue 3: Pods CrashLooping
```bash
# Check logs
kubectl logs <pod-name>

# Describe pod
kubectl describe pod <pod-name>

# Use kubectl-ai
kubectl-ai "why is my pod crashing"
```

### Issue 4: Service Not Accessible
```bash
# Check service
kubectl get svc

# Port forward
kubectl port-forward service/todo-frontend 3000:80

# Or use minikube tunnel
minikube tunnel
```

---

## 📊 Resource Requirements

**Minimum System Requirements:**
- RAM: 4GB (8GB recommended)
- Disk: 20GB free space
- CPU: 2 cores
- Docker installed and running

**Minikube Configuration:**
```bash
# Recommended settings
minikube start \
  --driver=docker \
  --memory=2048mb \
  --cpus=2 \
  --disk-size=20g
```

---

## 🎉 Success Criteria

Phase IV is complete when:

✅ Minikube running
✅ Dockerfiles working
✅ Images built successfully
✅ Helm deployment successful
✅ All pods running (2/2 ready)
✅ Services accessible
✅ kubectl-ai examples working
✅ Documentation complete
✅ Demo video recorded
✅ GitHub updated with tag

---

## 📈 Points Breakdown

**Phase IV Total: 250 points**

- Dockerfiles (50 pts)
- Helm Charts (50 pts)
- Minikube Deployment (75 pts)
- kubectl-ai Usage (25 pts)
- kagent Usage (25 pts)
- Documentation (25 pts)

**Bonus Opportunities:**
- Gordon (Docker AI) usage: +50 pts
- Advanced Helm features: +25 pts
- Monitoring setup: +25 pts

---

## 🚀 Next Steps

After Phase IV is complete:

1. Tag the commit: `git tag -a phase-iv -m "Phase IV complete"`
2. Push to GitHub: `git push origin phase-iv`
3. Record demo video
4. Fill submission form
5. Prepare for Phase V (Cloud deployment)

---

**Phase IV Status:** ⚠️ **85% Complete**

**Remaining:**
- Test Minikube deployment
- Create kubectl-ai/kagent documentation
- Record demo video
- Submit!

Good luck! 🎉
