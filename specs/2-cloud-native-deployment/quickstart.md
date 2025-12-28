# Quickstart: Cloud-Native Deployment (Phase V)

**Feature**: 2-cloud-native-deployment
**Prerequisites**: Phase I-IV completed, Docker, kubectl, Helm, Dapr CLI installed

---

## Local Development (Minikube)

### 1. Start Minikube

```bash
# Start Minikube with sufficient resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Verify cluster
kubectl cluster-info
```

### 2. Initialize Dapr on Kubernetes

```bash
# Install Dapr control plane
dapr init -k

# Verify Dapr installation
dapr status -k

# Expected output:
#   dapr-operator: Running
#   dapr-sidecar-injector: Running
#   dapr-sentry: Running
#   dapr-placement-server: Running
```

### 3. Setup Redpanda Cloud (Kafka)

```bash
# Sign up at https://redpanda.com/try-redpanda
# Create cluster and get connection details

# Save credentials in Kubernetes Secret
kubectl create secret generic dapr-secrets \
  --from-literal=kafka-username='your-username' \
  --from-literal=kafka-password='your-password' \
  --from-literal=postgres-connection-string='postgresql://user:pass@neon.tech/db' \
  --from-literal=sendgrid-api-key='SG.xxx'
```

### 4. Deploy Dapr Components

```bash
# Apply Dapr component configurations
kubectl apply -f kubernetes/dapr-components/

# Verify components
dapr components -k
```

### 5. Build Docker Images

```bash
# Build all microservices
docker build -t todo-api-gateway:v1 -f services/api-gateway/Dockerfile .
docker build -t todo-task-service:v1 -f services/task-service/Dockerfile .
docker build -t todo-scheduler-service:v1 -f services/scheduler-service/Dockerfile .
docker build -t todo-notification-service:v1 -f services/notification-service/Dockerfile .

# Load images into Minikube
minikube image load todo-api-gateway:v1
minikube image load todo-task-service:v1
minikube image load todo-scheduler-service:v1
minikube image load todo-notification-service:v1
```

### 6. Deploy with Helm

```bash
# Install Helm chart (umbrella chart with all services)
helm install todo-app helm/todo-app \
  --values helm/todo-app/values-dev.yaml \
  --namespace default \
  --create-namespace

# Watch pod startup
kubectl get pods -w

# Expected pods:
#   todo-api-gateway-xxx (2 containers: app + dapr-sidecar)
#   todo-task-service-xxx (2 containers)
#   todo-scheduler-service-xxx (2 containers)
#   todo-notification-service-xxx (2 containers)
```

### 7. Test Deployment

```bash
# Port-forward API Gateway
kubectl port-forward svc/todo-api-gateway 8000:8000

# Test health endpoint
curl http://localhost:8000/health

# Create a task
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add task: buy groceries"}'

# Check Kafka events
kubectl logs -l app=task-service -c daprd --tail=50 | grep pubsub
```

### 8. Access Logs and Metrics

```bash
# View application logs
kubectl logs -l app=task-service -c task-service

# View Dapr sidecar logs
kubectl logs -l app=task-service -c daprd

# Access Dapr dashboard (optional)
dapr dashboard -k -p 9999
# Open http://localhost:9999
```

---

## Cloud Deployment (DOKS / GKE / AKS)

### Option 1: DigitalOcean Kubernetes (DOKS)

```bash
# Install doctl CLI
# https://docs.digitalocean.com/reference/doctl/how-to/install/

# Authenticate
doctl auth init

# Create Kubernetes cluster (3 nodes, 4GB RAM each)
doctl kubernetes cluster create todo-prod \
  --region nyc1 \
  --size s-2vcpu-4gb \
  --count 3

# Get kubeconfig
doctl kubernetes cluster kubeconfig save todo-prod

# Verify connection
kubectl cluster-info

# Initialize Dapr
dapr init -k

# Create secrets
kubectl create secret generic dapr-secrets \
  --from-literal=kafka-username='prod-username' \
  --from-literal=kafka-password='prod-password' \
  --from-literal=postgres-connection-string='prod-db-url' \
  --from-literal=sendgrid-api-key='prod-sendgrid-key'

# Deploy Dapr components
kubectl apply -f kubernetes/dapr-components/

# Deploy application (use production values)
helm install todo-app helm/todo-app \
  --values helm/todo-app/values-prod.yaml \
  --namespace production \
  --create-namespace

# Expose API Gateway via LoadBalancer
kubectl expose deployment todo-api-gateway \
  --type=LoadBalancer \
  --port=80 \
  --target-port=8000 \
  --namespace production

# Get external IP
kubectl get svc todo-api-gateway -n production
```

### Option 2: Google Kubernetes Engine (GKE)

```bash
# Install gcloud CLI
# https://cloud.google.com/sdk/docs/install

# Authenticate
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# Create GKE cluster
gcloud container clusters create todo-prod \
  --region us-central1 \
  --num-nodes 3 \
  --machine-type e2-standard-2

# Get credentials
gcloud container clusters get-credentials todo-prod --region us-central1

# Follow same steps as DOKS (Dapr init, secrets, deploy)
```

### Option 3: Azure Kubernetes Service (AKS)

```bash
# Install Azure CLI
# https://learn.microsoft.com/en-us/cli/azure/install-azure-cli

# Authenticate
az login

# Create resource group
az group create --name todo-rg --location eastus

# Create AKS cluster
az aks create \
  --resource-group todo-rg \
  --name todo-prod \
  --node-count 3 \
  --node-vm-size Standard_D2s_v3 \
  --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group todo-rg --name todo-prod

# Follow same steps as DOKS (Dapr init, secrets, deploy)
```

---

## Monitoring Setup (Prometheus + Grafana)

### Install kube-prometheus-stack

```bash
# Add Prometheus Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus + Grafana
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false

# Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=grafana -n monitoring --timeout=300s
```

### Access Grafana

```bash
# Port-forward Grafana
kubectl port-forward svc/monitoring-grafana 3000:80 -n monitoring

# Get admin password
kubectl get secret monitoring-grafana -n monitoring -o jsonpath="{.data.admin-password}" | base64 -d

# Open http://localhost:3000
# Username: admin
# Password: <from above command>
```

### Import Dapr Dashboards

1. In Grafana, go to Dashboards → Import
2. Import Dapr System Dashboard: ID **14456**
3. Import Dapr Sidecar Dashboard: ID **19837**
4. Create custom dashboard for business metrics (tasks created, reminders sent)

---

## CI/CD Setup (GitHub Actions)

### Prerequisites

1. Docker Hub account or GitHub Container Registry
2. Kubernetes cluster with kubectl access
3. GitHub repository secrets configured

### Configure GitHub Secrets

```bash
# In GitHub repo: Settings → Secrets and variables → Actions

# Add these secrets:
DOCKER_USERNAME=your-dockerhub-username
DOCKER_PASSWORD=your-dockerhub-token
KUBE_CONFIG=<base64-encoded-kubeconfig>
DATABASE_URL=postgresql://...
OPENAI_API_KEY=sk-...
KAFKA_USERNAME=redpanda-user
KAFKA_PASSWORD=redpanda-pass
SENDGRID_API_KEY=SG.xxx
```

### Trigger Deployment

```bash
# Push to main branch triggers CI/CD
git add .
git commit -m "Deploy Phase V to production"
git push origin main

# Monitor workflow in GitHub Actions tab
# Workflow will:
# 1. Run tests
# 2. Build Docker images
# 3. Push to registry
# 4. Deploy to Kubernetes with Helm
# 5. Run smoke tests
```

---

## Troubleshooting

### Pods not starting

```bash
# Check pod events
kubectl describe pod <pod-name>

# Common issues:
# - ImagePullBackOff: Image not in registry or wrong tag
# - CrashLoopBackOff: Application error, check logs
# - Pending: Insufficient resources, scale down or add nodes
```

### Dapr sidecar not injecting

```bash
# Verify Dapr installation
dapr status -k

# Check pod annotations
kubectl get pod <pod-name> -o yaml | grep dapr

# Required annotations:
#   dapr.io/enabled: "true"
#   dapr.io/app-id: "task-service"
#   dapr.io/app-port: "8000"
```

### Kafka connection issues

```bash
# Check Dapr component logs
kubectl logs -l dapr.io/app-id=task-service -c daprd

# Test Kafka connection from pod
kubectl exec -it <pod-name> -c task-service -- sh
# Inside pod:
pip install kafka-python
python3 -c "from kafka import KafkaProducer; producer = KafkaProducer(bootstrap_servers='bootstrap.redpanda.cloud:9092')"
```

### Database connection issues

```bash
# Verify secret exists
kubectl get secret dapr-secrets -o yaml

# Check connection string format
kubectl get secret dapr-secrets -o jsonpath='{.data.postgres-connection-string}' | base64 -d

# Test from pod
kubectl exec -it <pod-name> -c task-service -- sh
pip install psycopg2-binary
python3 -c "import psycopg2; conn = psycopg2.connect('CONNECTION_STRING')"
```

---

## Cleanup

### Minikube

```bash
# Delete Helm release
helm uninstall todo-app

# Delete Dapr
dapr uninstall -k

# Stop Minikube
minikube stop

# Delete cluster (optional)
minikube delete
```

### Cloud (DOKS)

```bash
# Delete Helm release
helm uninstall todo-app -n production

# Delete cluster
doctl kubernetes cluster delete todo-prod
```

### Cloud (GKE)

```bash
helm uninstall todo-app -n production
gcloud container clusters delete todo-prod --region us-central1
```

### Cloud (AKS)

```bash
helm uninstall todo-app -n production
az aks delete --resource-group todo-rg --name todo-prod
az group delete --name todo-rg
```

---

## Next Steps

1. Review [plan.md](./plan.md) for architecture details
2. Check [data-model.md](./data-model.md) for entity relationships
3. Implement tasks from [tasks.md](./tasks.md) (generated by `/sp.tasks`)
4. Monitor metrics in Grafana dashboards
5. Set up alerts in Prometheus AlertManager
6. Configure backup and disaster recovery
7. Document runbooks for common operations

---

**Status**: Phase 1 Complete | Ready for `/sp.tasks`
