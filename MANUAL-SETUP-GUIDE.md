# Complete Manual Setup Guide - Phase V Deployment

Step-by-step guide for manually deploying Phase V (Cloud-Native Microservices).

## Part 1: Install Required Software (30-40 minutes)

### Step 1: Install Docker Desktop
**Time: ~10 minutes**

1. **Download Docker Desktop:**
   - Windows/Mac: https://www.docker.com/products/docker-desktop/
   - Linux: https://docs.docker.com/engine/install/ubuntu/

2. **Install and Start Docker:**
   ```bash
   # After installation, verify Docker is running
   docker --version
   docker ps
   ```

   Expected output:
   ```
   Docker version 24.x.x
   CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
   ```

3. **Troubleshooting:**
   - If Docker doesn't start, restart your computer
   - On Windows, enable WSL2 if prompted
   - On Linux, add your user to docker group: `sudo usermod -aG docker $USER`

---

### Step 2: Install Minikube
**Time: ~10 minutes**

1. **Install Minikube:**

   **Linux:**
   ```bash
   curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
   sudo install minikube-linux-amd64 /usr/local/bin/minikube
   ```

   **Windows (PowerShell as Admin):**
   ```powershell
   choco install minikube
   # Or download from: https://minikube.sigs.k8s.io/docs/start/
   ```

   **Mac:**
   ```bash
   brew install minikube
   ```

2. **Verify Installation:**
   ```bash
   minikube version
   ```

3. **Start Minikube:**
   ```bash
   minikube start --driver=docker --cpus=4 --memory=8192
   ```

   This will take 5-10 minutes. You'll see:
   ```
   😄  minikube v1.x.x on Ubuntu
   ✨  Using the docker driver
   👍  Starting control plane node minikube
   🔥  Creating docker container
   🐳  Preparing Kubernetes v1.x.x
   🔎  Verifying Kubernetes components
   🌟  Enabled addons: storage-provisioner, default-storageclass
   🏄  Done! kubectl is now configured
   ```

4. **Verify Minikube:**
   ```bash
   minikube status
   kubectl cluster-info
   kubectl get nodes
   ```

   Expected:
   ```
   minikube
   type: Control Plane
   host: Running
   kubelet: Running
   ```

---

### Step 3: Install kubectl (if not already installed)
**Time: ~3 minutes**

1. **Check if kubectl is installed:**
   ```bash
   kubectl version --client
   ```

2. **If not installed:**

   **Linux:**
   ```bash
   curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
   sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
   ```

   **Windows (PowerShell as Admin):**
   ```powershell
   choco install kubernetes-cli
   ```

   **Mac:**
   ```bash
   brew install kubectl
   ```

3. **Verify:**
   ```bash
   kubectl version --client
   kubectl get nodes
   ```

---

### Step 4: Install Dapr CLI
**Time: ~5 minutes**

1. **Install Dapr CLI:**

   **Linux/Mac:**
   ```bash
   wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash
   ```

   **Windows (PowerShell as Admin):**
   ```powershell
   powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"
   ```

2. **Verify Dapr CLI:**
   ```bash
   dapr --version
   ```

3. **Initialize Dapr on Kubernetes:**
   ```bash
   dapr init --kubernetes --wait
   ```

   This takes 2-3 minutes. You'll see:
   ```
   ⌛  Making the jump to hyperspace...
   ✅  Deploying the Dapr control plane to your cluster...
   ✅  Success! Dapr has been installed to namespace dapr-system
   ```

4. **Verify Dapr installation:**
   ```bash
   dapr status -k
   kubectl get pods -n dapr-system
   ```

   You should see 4 pods running:
   ```
   NAME                                    READY   STATUS    RESTARTS   AGE
   dapr-dashboard-xxx                      1/1     Running   0          2m
   dapr-operator-xxx                       1/1     Running   0          2m
   dapr-placement-server-xxx               1/1     Running   0          2m
   dapr-sidecar-injector-xxx              1/1     Running   0          2m
   ```

---

### Step 5: Install Helm
**Time: ~3 minutes**

1. **Install Helm:**

   **Linux:**
   ```bash
   curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
   ```

   **Windows (PowerShell as Admin):**
   ```powershell
   choco install kubernetes-helm
   ```

   **Mac:**
   ```bash
   brew install helm
   ```

2. **Verify:**
   ```bash
   helm version
   ```

---

## Part 2: Setup External Services (20-30 minutes)

### Step 6: Setup Redpanda Cloud Kafka (T009)
**Time: ~10 minutes**

1. **Sign up for Redpanda Cloud:**
   - Go to: https://redpanda.com/try-redpanda
   - Click "Start Free"
   - Sign up with Google/GitHub or email

2. **Create a Cluster:**
   - Click "Create Cluster"
   - Choose "Serverless" (free tier)
   - Name: `todo-chatbot-kafka`
   - Region: Choose closest to you
   - Click "Create"
   - Wait 3-5 minutes for cluster to provision

3. **Create a User:**
   - Click on your cluster
   - Go to "Security" → "Users"
   - Click "Create User"
   - Username: `todo-app-user`
   - Password: Generate a strong password (save it!)
   - Mechanism: SCRAM-SHA-256
   - Click "Create"

4. **Get Bootstrap Servers:**
   - Go to "Overview" tab
   - Copy "Bootstrap servers" URL
   - Format: `seed-xxxxx.cloud.redpanda.com:9092`
   - **Save this URL - you'll need it!**

5. **Create Topics (Optional - Dapr will auto-create):**
   - Go to "Topics" tab
   - You can manually create topics or let Dapr create them:
     - `task.created`
     - `task.completed`
     - `task.deleted`
     - `recurring-task.created`
     - `reminder.triggered`

---

### Step 7: Setup SendGrid for Email
**Time: ~5 minutes**

1. **Sign up for SendGrid:**
   - Go to: https://sendgrid.com/
   - Click "Start for Free"
   - Complete signup (free tier allows 100 emails/day)

2. **Create API Key:**
   - After login, go to Settings → API Keys
   - Click "Create API Key"
   - Name: `todo-chatbot-notifications`
   - Permissions: "Restricted Access" → Select "Mail Send" → Full Access
   - Click "Create & View"
   - **Copy the API key - you won't see it again!**
   - Format: `SG.xxxxxxxxxxxxxxxxxxxxxxxx`

3. **Verify Sender Email (Important!):**
   - Go to Settings → Sender Authentication
   - Click "Verify a Single Sender"
   - Enter your email address
   - Check your email and click verification link
   - **This is required for emails to work!**

---

### Step 8: Get Neon PostgreSQL URL
**Time: ~2 minutes**

1. **You already have Neon from previous phases, but verify:**
   - Go to: https://console.neon.tech/
   - Select your project
   - Go to "Dashboard"
   - Copy "Connection String"
   - Format: `postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require`

2. **For Dapr State Store, convert to asyncpg format:**
   - Change `postgresql://` to `postgresql+asyncpg://`
   - Example:
     ```
     Original: postgresql://user:pass@host/db
     For Dapr: postgresql+asyncpg://user:pass@host/db
     ```

---

### Step 9: Get OpenAI API Key
**Time: ~2 minutes**

1. **You already have this from previous phases:**
   - Go to: https://platform.openai.com/api-keys
   - Copy your existing API key or create new one
   - Format: `sk-proj-xxxxxxxxxxxxx`

---

### Step 10: Generate Better Auth Secret
**Time: ~1 minute**

```bash
# Generate a random 32-character secret
openssl rand -hex 32
```

Save the output - this is your `BETTER_AUTH_SECRET`

---

## Part 3: Configure Kubernetes Secrets (T042)
**Time: ~5 minutes**

### Step 11: Create secrets-local.yaml

1. **Copy the template:**
   ```bash
   cd /home/umair/todo-chatbot
   cp kubernetes/base/secrets.yaml kubernetes/base/secrets-local.yaml
   ```

2. **Edit the file:**
   ```bash
   nano kubernetes/base/secrets-local.yaml
   # Or use VS Code: code kubernetes/base/secrets-local.yaml
   ```

3. **Replace ALL placeholders with your actual values:**

   ```yaml
   apiVersion: v1
   kind: Secret
   metadata:
     name: todo-secrets
     namespace: todo-app
   type: Opaque
   stringData:
     # Neon PostgreSQL (convert to asyncpg format)
     DATABASE_URL: "postgresql+asyncpg://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require"

     # Redpanda Cloud Kafka
     KAFKA_BOOTSTRAP_SERVERS: "seed-xxxxx.cloud.redpanda.com:9092"
     KAFKA_SASL_USERNAME: "todo-app-user"
     KAFKA_SASL_PASSWORD: "your-redpanda-password"

     # SendGrid
     SENDGRID_API_KEY: "SG.xxxxxxxxxxxxxxxxxxxxxxxx"

     # OpenAI
     OPENAI_API_KEY: "sk-proj-xxxxxxxxxxxxx"

     # Better Auth
     BETTER_AUTH_SECRET: "your-32-character-secret-from-openssl"
     BETTER_AUTH_ISSUER: "todo-chatbot"
   ```

4. **Save and close:**
   - In nano: `Ctrl+X`, then `Y`, then `Enter`
   - In VS Code: `Ctrl+S`

5. **IMPORTANT: Never commit secrets-local.yaml to git!**
   ```bash
   # Add to .gitignore (already done in project)
   echo "kubernetes/base/secrets-local.yaml" >> .gitignore
   ```

---

## Part 4: Build and Deploy (T039-T043)
**Time: ~15-20 minutes**

### Step 12: Build Docker Images (T039)
**Time: ~5-10 minutes**

1. **Navigate to project directory:**
   ```bash
   cd /home/umair/todo-chatbot
   ```

2. **Run build script:**
   ```bash
   ./build-images.sh
   ```

   You'll see output like:
   ```
   🐳 Building Docker images for Todo Chatbot microservices...
   📦 Building API Gateway...
   [+] Building 45.2s (12/12) FINISHED
   📦 Building Task Service...
   [+] Building 38.5s (12/12) FINISHED
   📦 Building Scheduler Service...
   [+] Building 35.1s (12/12) FINISHED
   📦 Building Notification Service...
   [+] Building 33.8s (12/12) FINISHED
   ✅ All Docker images built successfully!
   ```

3. **Verify images:**
   ```bash
   docker images | grep todo-
   ```

   You should see 4 images:
   ```
   todo-api-gateway           v1
   todo-task-service          v1
   todo-scheduler-service     v1
   todo-notification-service  v1
   ```

4. **If build fails:**
   - Check Docker is running: `docker ps`
   - Check for syntax errors in Dockerfiles
   - Try building individually:
     ```bash
     docker build -t todo-api-gateway:v1 services/api-gateway
     ```

---

### Step 13: Load Images into Minikube (T040)
**Time: ~3-5 minutes**

1. **Run load script:**
   ```bash
   ./load-images-minikube.sh
   ```

   Output:
   ```
   🚀 Loading Docker images into Minikube...
   📦 Loading API Gateway image...
   📦 Loading Task Service image...
   📦 Loading Scheduler Service image...
   📦 Loading Notification Service image...
   ✅ All images loaded into Minikube!
   ```

2. **Verify images in Minikube:**
   ```bash
   minikube image ls | grep todo-
   ```

3. **Alternative manual method (if script fails):**
   ```bash
   minikube image load todo-api-gateway:v1
   minikube image load todo-task-service:v1
   minikube image load todo-scheduler-service:v1
   minikube image load todo-notification-service:v1
   ```

---

### Step 14: Deploy to Kubernetes (T041-T043)
**Time: ~5 minutes**

1. **Run deployment script:**
   ```bash
   ./deploy-k8s.sh
   ```

   This will:
   - Create `todo-app` namespace
   - Deploy secrets (T042)
   - Deploy Dapr components (T041)
   - Deploy services with Helm (T043)

   Output:
   ```
   ☸️  Deploying Todo Chatbot to Kubernetes...
   📦 Creating namespace 'todo-app'...
   namespace/todo-app created
   🔐 Deploying Kubernetes secrets...
   secret/todo-secrets created
   🎯 Deploying Dapr components...
   component.dapr.io/statestore created
   component.dapr.io/pubsub created
   component.dapr.io/secretstore created
   component.dapr.io/email-binding created
   component.dapr.io/cron-binding created
   📦 Deploying services with Helm...
   Release "todo-app" does not exist. Installing it now.
   NAME: todo-app
   STATUS: deployed
   ✅ Deployment complete!
   ```

2. **Check pod status:**
   ```bash
   kubectl get pods -n todo-app
   ```

   Wait until all pods show `2/2 READY`:
   ```
   NAME                              READY   STATUS    RESTARTS   AGE
   api-gateway-xxx                   2/2     Running   0          2m
   task-service-xxx                  2/2     Running   0          2m
   scheduler-service-xxx             2/2     Running   0          2m
   notification-service-xxx          2/2     Running   0          2m
   ```

   The `2/2` means:
   - 1st container: Your service
   - 2nd container: Dapr sidecar

3. **If pods are not ready:**
   ```bash
   # Check pod details
   kubectl describe pod -n todo-app <pod-name>

   # Check logs
   kubectl logs -n todo-app <pod-name> -c <service-name>
   kubectl logs -n todo-app <pod-name> -c daprd
   ```

4. **Manual deployment (if script fails):**
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
       --wait --timeout 5m
   ```

---

## Part 5: Testing and Verification (T044-T047)
**Time: ~10 minutes**

### Step 15: Verify Pods with Dapr Sidecars (T044)
**Time: ~2 minutes**

1. **Check all pods are running:**
   ```bash
   kubectl get pods -n todo-app
   ```

   All should show `2/2 READY`

2. **Verify Dapr sidecars:**
   ```bash
   kubectl get pods -n todo-app -o custom-columns='NAME:.metadata.name,CONTAINERS:.spec.containers[*].name'
   ```

   Output should show 2 containers per pod:
   ```
   NAME                              CONTAINERS
   api-gateway-xxx                   api-gateway,daprd
   task-service-xxx                  task-service,daprd
   ```

3. **Check Dapr components:**
   ```bash
   kubectl get components -n todo-app
   ```

   Should show 5 components:
   ```
   NAME             AGE
   statestore       2m
   pubsub           2m
   secretstore      2m
   email-binding    2m
   cron-binding     2m
   ```

---

### Step 16: Test API Gateway Health (T045)
**Time: ~3 minutes**

1. **Setup port-forward (in a separate terminal):**
   ```bash
   kubectl port-forward -n todo-app svc/api-gateway 8000:8000
   ```

   Keep this running. You'll see:
   ```
   Forwarding from 127.0.0.1:8000 -> 8000
   Forwarding from [::1]:8000 -> 8000
   ```

2. **Test health endpoint (in another terminal):**
   ```bash
   curl http://localhost:8000/health
   ```

   Expected response:
   ```json
   {
     "status": "healthy",
     "service": "api-gateway",
     "version": "1.0.0",
     "environment": "development"
   }
   ```

3. **If health check fails:**
   ```bash
   # Check API Gateway logs
   kubectl logs -n todo-app -l app=api-gateway -c api-gateway

   # Check Dapr sidecar logs
   kubectl logs -n todo-app -l app=api-gateway -c daprd
   ```

---

### Step 17: Test Task Creation and Kafka Events (T046)
**Time: ~5 minutes**

1. **Create a test task (with port-forward still running):**
   ```bash
   curl -X POST http://localhost:8000/tasks \
       -H "Content-Type: application/json" \
       -H "Authorization: Bearer test-token" \
       -d '{
           "title": "Test Task from Manual Deployment",
           "user_id": "test-user-123"
       }'
   ```

   Expected response:
   ```json
   {
     "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
     "user_id": "test-user-123",
     "title": "Test Task from Manual Deployment",
     "completed": false,
     "created_at": "2025-12-29T...",
     "completed_at": null
   }
   ```

2. **Check Task Service logs for event publishing:**
   ```bash
   kubectl logs -n todo-app -l app=task-service -c task-service --tail=50
   ```

   Look for:
   ```
   📤 Published task.created event: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
   ```

3. **Check Dapr logs for Kafka publishing:**
   ```bash
   kubectl logs -n todo-app -l app=task-service -c daprd --tail=50
   ```

   Look for Kafka-related messages (if Kafka is properly configured)

4. **Run automated test script:**
   ```bash
   ./test-deployment.sh
   ```

   This runs all tests (T044-T046) automatically

---

### Step 18: Test Pod Restart and Recovery (T047)
**Time: ~2 minutes**

1. **Delete a pod to test auto-restart:**
   ```bash
   kubectl delete pod -n todo-app -l app=task-service
   ```

2. **Watch pod restart:**
   ```bash
   kubectl get pods -n todo-app -w
   ```

   You'll see:
   ```
   task-service-xxx   2/2   Running   0   5m
   task-service-xxx   2/2   Terminating   0   5m
   task-service-xxx   0/2   Pending       0   0s
   task-service-xxx   0/2   Init:0/1      0   1s
   task-service-xxx   2/2   Running       0   10s
   ```

3. **Press Ctrl+C to stop watching**

4. **Verify service recovered:**
   ```bash
   kubectl get pods -n todo-app
   ```

   All pods should be `2/2 READY` again

5. **Test API still works:**
   ```bash
   curl http://localhost:8000/health
   ```

---

## Part 6: Troubleshooting Common Issues

### Issue 1: Pods stuck in "Pending" or "ImagePullBackOff"

**Symptoms:**
```bash
kubectl get pods -n todo-app
NAME                    READY   STATUS              RESTARTS   AGE
task-service-xxx        0/2     ImagePullBackOff    0          2m
```

**Solution:**
```bash
# Check pod events
kubectl describe pod -n todo-app task-service-xxx

# Common fixes:
# 1. Reload images into Minikube
./load-images-minikube.sh

# 2. Update Helm values to use correct image pull policy
helm upgrade todo-app ./helm/todo-app \
    --namespace todo-app \
    --values ./helm/todo-app/values-dev.yaml \
    --set apiGateway.image.pullPolicy=Never \
    --set taskService.image.pullPolicy=Never \
    --set schedulerService.image.pullPolicy=Never \
    --set notificationService.image.pullPolicy=Never \
    --wait
```

---

### Issue 2: Pods running but health check fails

**Symptoms:**
```bash
curl http://localhost:8000/health
curl: (7) Failed to connect to localhost port 8000
```

**Solution:**
```bash
# 1. Check if port-forward is running
ps aux | grep port-forward

# 2. Check pod logs for errors
kubectl logs -n todo-app -l app=api-gateway -c api-gateway

# 3. Check service exists
kubectl get svc -n todo-app

# 4. Try direct pod access
POD_NAME=$(kubectl get pod -n todo-app -l app=api-gateway -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n todo-app $POD_NAME -c api-gateway -- curl localhost:8000/health
```

---

### Issue 3: Secrets not loading

**Symptoms:**
```
Error: secret "todo-secrets" not found
```

**Solution:**
```bash
# 1. Check secret exists
kubectl get secret -n todo-app

# 2. If missing, create it
kubectl apply -f kubernetes/base/secrets-local.yaml -n todo-app

# 3. Verify secret data
kubectl describe secret todo-secrets -n todo-app

# 4. Restart pods to pick up secrets
kubectl rollout restart deployment -n todo-app
```

---

### Issue 4: Kafka events not publishing

**Symptoms:**
No event logs in Dapr sidecar

**Solution:**
```bash
# 1. Check Dapr pub/sub component
kubectl describe component pubsub -n todo-app

# 2. Check for errors in Dapr logs
kubectl logs -n todo-app -l app=task-service -c daprd | grep -i error

# 3. Verify Kafka credentials in secret
kubectl get secret todo-secrets -n todo-app -o jsonpath='{.data.KAFKA_BOOTSTRAP_SERVERS}' | base64 -d

# 4. Test Dapr health
kubectl exec -n todo-app <pod-name> -c daprd -- wget -O- http://localhost:3500/v1.0/healthz
```

---

### Issue 5: Minikube out of resources

**Symptoms:**
```
Insufficient cpu, memory
```

**Solution:**
```bash
# 1. Check Minikube resources
minikube status

# 2. Restart with more resources
minikube stop
minikube delete
minikube start --driver=docker --cpus=4 --memory=10240

# 3. Redeploy
./load-images-minikube.sh
./deploy-k8s.sh
```

---

## Part 7: Cleanup and Next Steps

### To Stop Services (but keep Minikube)
```bash
# Delete deployment
helm uninstall todo-app -n todo-app

# Delete namespace
kubectl delete namespace todo-app
```

### To Fully Clean Up
```bash
# Uninstall everything
helm uninstall todo-app -n todo-app
kubectl delete namespace todo-app
dapr uninstall --kubernetes

# Stop Minikube
minikube stop

# Delete Minikube (removes all data)
minikube delete
```

### Next: Deploy to Cloud (T048)

Once local testing works, deploy to cloud:
- See DEPLOYMENT-PHASE-V.md for AWS EKS, Google GKE, Azure AKS instructions

---

## Summary Checklist

- [ ] Part 1: Install Docker, Minikube, kubectl, Dapr, Helm ✅
- [ ] Part 2: Setup Redpanda, SendGrid, secrets ✅
- [ ] Part 3: Configure secrets-local.yaml ✅
- [ ] Part 4: Build images, load to Minikube, deploy ✅
- [ ] Part 5: Test pods, health, events, recovery ✅
- [ ] Part 6: Troubleshoot any issues ✅
- [ ] Part 7: Deploy to cloud (optional) ⏳

**Your current progress: 38/113 tasks (34%)**

Good luck! 🚀
