# kubectl-ai Usage Examples for Phase IV

## Overview
This document demonstrates the usage of kubectl-ai for AI-assisted Kubernetes operations in the Todo AI Chatbot Phase IV deployment.

---

## Installation

```bash
# Install kubectl-ai (if not already installed)
pip install kubectl-ai

# Configure with OpenAI API key
kubectl-ai config set-key YOUR_OPENAI_API_KEY
```

---

## 1. Deployment Operations

### Show All Pods
```bash
kubectl-ai "show me all pods in the todo-app namespace"
```

**Expected AI Response:**
```
Here are all the pods in the todo-app namespace:

NAME                            READY   STATUS    AGE
todo-frontend-7b586c76c-q49c7   1/1     Running   10m
todo-backend-686f55f7d-bpgjx    0/1     Error     15m

The frontend pod is running successfully.
The backend pod is in an error state and needs investigation.
```

### Check Deployment Status
```bash
kubectl-ai "what is the status of my deployments in todo-app"
```

**Expected AI Response:**
```
Your deployments in todo-app namespace:

todo-frontend: 1/1 replicas ready ✓
todo-backend: 0/1 replicas ready ✗

The frontend deployment is healthy.
The backend deployment has issues - the pod is failing.
```

---

## 2. Troubleshooting

### Diagnose Pod Failures
```bash
kubectl-ai "why is the todo-backend pod not running"
```

**Expected AI Response:**
```
Checking todo-backend pod...

The pod is in CrashLoopBackOff state. Checking logs...

Issue found: Container is crashing on startup.
Recommendation: Check logs with:
  kubectl logs todo-backend-686f55f7d-bpgjx -n todo-app

Common causes:
- Missing environment variables
- Application startup error
- Health check failures
```

### Check Resource Usage
```bash
kubectl-ai "show resource usage for all pods"
```

**Expected AI Response:**
```
Resource usage in todo-app namespace:

todo-frontend:
  CPU: 5m / 200m (2.5%)
  Memory: 15Mi / 256Mi (5.9%)
  Status: Healthy ✓

todo-backend:
  Pod not running - no metrics available
```

---

## 3. Service Operations

### List All Services
```bash
kubectl-ai "what services are exposed in todo-app"
```

**Expected AI Response:**
```
Services in todo-app namespace:

1. todo-frontend
   - Type: NodePort
   - ClusterIP: 10.110.25.103
   - Port: 80:30080/TCP
   - Accessible externally via NodePort

2. todo-backend
   - Type: ClusterIP
   - ClusterIP: 10.103.56.41
   - Port: 8000/TCP
   - Internal only
```

### Get Service Endpoints
```bash
kubectl-ai "how do I access the todo-frontend service"
```

**Expected AI Response:**
```
To access todo-frontend service:

Option 1: NodePort (current setup)
  URL: http://<node-ip>:30080
  For Minikube: minikube service todo-frontend --url -n todo-app

Option 2: Port Forwarding
  kubectl port-forward service/todo-frontend 3000:80 -n todo-app
  Then access: http://localhost:3000

Option 3: Minikube Tunnel
  minikube tunnel
  Then access via ClusterIP
```

---

## 4. Scaling Operations

### Scale Deployment
```bash
kubectl-ai "scale todo-frontend to 3 replicas"
```

**Expected AI Response:**
```
Scaling todo-frontend deployment to 3 replicas...

✓ Deployment scaled successfully

Before: 1 replica
After: 3 replicas

Verify with:
  kubectl get deployment todo-frontend -n todo-app
```

### Check Scaling Status
```bash
kubectl-ai "how many replicas are running for each deployment"
```

**Expected AI Response:**
```
Replica status:

todo-frontend: 3/3 ready
todo-backend: 0/1 ready

Recommendation: Backend needs attention before scaling.
```

---

## 5. Configuration Management

### View ConfigMaps
```bash
kubectl-ai "list all configmaps in todo-app"
```

### View Secrets
```bash
kubectl-ai "show secret names in todo-app namespace"
```

**Expected AI Response:**
```
Secrets in todo-app:
- todo-backend-secrets (Opaque, 4 keys)
- default-token-xxxxx (kubernetes.io/service-account-token)

Note: Actual secret values are protected and not displayed.
```

---

## 6. Health Checks

### Overall Cluster Health
```bash
kubectl-ai "is my cluster healthy"
```

**Expected AI Response:**
```
Cluster Health Check:

✓ Nodes: 1/1 Ready (minikube)
✓ Control Plane: Running
✓ Kube-system pods: All running
⚠ User workloads: 1 pod failing in todo-app

Overall Status: Mostly Healthy
Action needed: Fix todo-backend pod
```

### Check Pod Events
```bash
kubectl-ai "what recent events happened in todo-app"
```

**Expected AI Response:**
```
Recent events in todo-app namespace (last 5 minutes):

Warning: BackOff - Container todo-backend is in CrashLoopBackOff
Normal: Pulled - Container image already present on machine
Normal: Created - Created container todo-frontend
Normal: Started - Started container todo-frontend

Summary: Frontend stable, backend needs investigation
```

---

## 7. Update Operations

### Update Image Version
```bash
kubectl-ai "update todo-frontend image to version v2"
```

**Expected AI Response:**
```
Updating todo-frontend image...

Command to execute:
  kubectl set image deployment/todo-frontend \
    todo-frontend=todo-frontend:v2 -n todo-app

⚠ Note: Make sure the image exists in your registry first.

Rollout status will be:
  kubectl rollout status deployment/todo-frontend -n todo-app
```

### Rollback Deployment
```bash
kubectl-ai "rollback todo-frontend to previous version"
```

**Expected AI Response:**
```
Rolling back todo-frontend...

Command:
  kubectl rollout undo deployment/todo-frontend -n todo-app

This will revert to the previous deployment revision.
```

---

## 8. Namespace Management

### List All Namespaces
```bash
kubectl-ai "show all namespaces in the cluster"
```

**Expected AI Response:**
```
Namespaces in cluster:

1. default (Active)
2. kube-node-lease (Active)
3. kube-public (Active)
4. kube-system (Active) - System components
5. dapr-system (Active) - Dapr runtime
6. todo-app (Active) - Your application

Total: 6 namespaces
```

---

## 9. Logs and Debugging

### Retrieve Logs
```bash
kubectl-ai "show me the last 20 lines of frontend logs"
```

**Expected AI Response:**
```
Last 20 lines from todo-frontend:

[Output would show nginx access logs or application logs]

Command used:
  kubectl logs todo-frontend-7b586c76c-q49c7 \
    -n todo-app --tail=20
```

### Stream Logs
```bash
kubectl-ai "stream logs from todo-frontend"
```

**Expected AI Response:**
```
Streaming logs from todo-frontend...

Command:
  kubectl logs -f todo-frontend-7b586c76c-q49c7 -n todo-app

Press Ctrl+C to stop streaming.
```

---

## 10. Resource Cleanup

### Delete Specific Resources
```bash
kubectl-ai "delete the todo-backend deployment"
```

**Expected AI Response:**
```
⚠ This will delete the todo-backend deployment.

Command to execute:
  kubectl delete deployment todo-backend -n todo-app

Confirm before proceeding (y/n)?
```

### Cleanup Entire Namespace
```bash
kubectl-ai "remove all resources from todo-app namespace"
```

**Expected AI Response:**
```
⚠ WARNING: This will delete ALL resources in todo-app namespace!

Resources to be deleted:
- 2 deployments
- 2 services
- 2 replicasets
- 2 pods

Command:
  kubectl delete namespace todo-app

This action cannot be undone. Confirm? (y/n)
```

---

## 11. Advanced Queries

### Resource Optimization
```bash
kubectl-ai "suggest resource optimizations for my deployments"
```

**Expected AI Response:**
```
Resource Optimization Suggestions:

todo-frontend:
  Current: 100m CPU / 128Mi Memory
  Actual usage: 5m CPU / 15Mi Memory
  ✓ Well-optimized, no changes needed

todo-backend:
  Cannot analyze - pod not running
  Recommendation: Fix startup issues first

General:
- Consider enabling autoscaling for production
- Monitor actual usage over time before adjusting
```

### Security Recommendations
```bash
kubectl-ai "check security best practices for my deployments"
```

**Expected AI Response:**
```
Security Check:

✓ Non-root users (when configured)
✓ Dropped capabilities
⚠ Secrets in environment variables (consider using volumes)
⚠ No network policies defined
⚠ No pod security policies

Recommendations:
1. Implement network policies to restrict traffic
2. Use secret volumes instead of env vars
3. Enable pod security admission
4. Add resource quotas to namespace
```

---

## Benefits of Using kubectl-ai

1. **Natural Language**: No need to remember exact kubectl syntax
2. **Context-Aware**: Understands your cluster state and suggests relevant actions
3. **Error Prevention**: Warns about destructive operations
4. **Learning Tool**: Shows the actual kubectl commands it would run
5. **Troubleshooting**: Analyzes logs and events to diagnose issues

---

## Comparison: Traditional vs kubectl-ai

### Traditional kubectl:
```bash
kubectl get pods -n todo-app
kubectl describe pod todo-backend-686f55f7d-bpgjx -n todo-app
kubectl logs todo-backend-686f55f7d-bpgjx -n todo-app --tail=50
```

### With kubectl-ai:
```bash
kubectl-ai "why is my backend pod failing in todo-app"
```

The AI automatically:
- Lists pods
- Identifies the failing pod
- Checks logs
- Analyzes events
- Provides recommendations

---

## Tips for Effective kubectl-ai Usage

1. **Be Specific**: Include namespace names and resource types
2. **Ask Why**: Use "why" questions for troubleshooting
3. **Request Explanations**: Ask for "explain" to understand outputs
4. **Combine Operations**: Ask for multi-step operations in one query
5. **Verify Commands**: Review the suggested commands before executing

---

**Phase IV Documentation**
**Created:** December 31, 2025
**Todo AI Chatbot** - Kubernetes Deployment
