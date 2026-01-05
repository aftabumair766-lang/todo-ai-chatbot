# Phase V - Next Steps (Quick Reference) 🎯

## Current Status: 90% Complete ✅

**All code is implemented and ready!** Just need Kafka credentials to activate.

---

## ⚡ Quick Start (When You Have Credentials)

### You Need:
- ✅ Bootstrap Server: `d5bd76jrcoacstiscs80.any.us-east-1.mpx.prd.cloud.redpanda.com:9092`
- ❌ SASL Username: `<GET FROM REDPANDA>`
- ❌ SASL Password: `<GET FROM REDPANDA>`

### Where to Get Credentials:

**Option A: Redpanda Console**
1. Login: https://cloud.redpanda.com
2. Click your cluster
3. Go to **"Connect"** or **"Security"** tab
4. Look for **"API Keys"** or **"Credentials"**
5. Click **"Create API Key"**
6. Copy username + password

**Option B: Upstash Kafka (Easier Alternative)**
1. Signup: https://upstash.com/
2. Create Kafka cluster (FREE tier)
3. Credentials shown immediately on dashboard
4. Use REST API endpoint provided

---

## 🚀 Deploy in 3 Steps (15 minutes total)

### Step 1: Configure Kafka (5 mins)
```bash
# Copy template
cp kubernetes/dapr-components/pubsub-kafka.yaml.template \
   kubernetes/dapr-components/pubsub-kafka.yaml

# Edit with your real credentials
nano kubernetes/dapr-components/pubsub-kafka.yaml

# Replace these three placeholders:
# - YOUR_BOOTSTRAP_SERVER → d5bd76jrcoacstiscs80.any.us-east-1.mpx.prd.cloud.redpanda.com:9092
# - YOUR_SASL_USERNAME → <your-username>
# - YOUR_SASL_PASSWORD → <your-password>
```

### Step 2: Create Kafka Topics (2 mins)
In Redpanda Console:
- Create topic: `task-events`
- Create topic: `tag-events`
- Create topic: `reminder-events`

Settings: 1 partition, 7 days retention

### Step 3: Deploy (8 mins)
```bash
# Run automated deployment script
./scripts/deploy-phase5.sh

# The script will:
# - Build Docker image with Dapr SDK
# - Apply Kafka component
# - Deploy with Dapr sidecar
# - Verify everything is working
```

---

## ✅ What's Already Done

### Code (100%)
- ✅ Event publisher module (`backend/events/publisher.py`)
- ✅ Integration in all CRUD operations (add, update, complete, delete)
- ✅ Dapr SDK added to requirements
- ✅ Error handling and fallback logic
- ✅ Event schemas defined

### Infrastructure (100%)
- ✅ Dapr annotations in deployments
- ✅ Kafka component template
- ✅ Kubernetes manifests updated
- ✅ Security configured (.gitignore)

### Documentation (100%)
- ✅ Implementation guide (PHASE_V_IMPLEMENTATION.md)
- ✅ Setup instructions (kubernetes/dapr-components/README.md)
- ✅ Deployment automation (scripts/deploy-phase5.sh)
- ✅ Event schemas documented

---

## 🧪 Testing After Deployment

### Test 1: Verify Dapr Sidecar
```bash
kubectl get pods -n todo-app
# Should show: todo-backend-xxx  2/2  Running
```

### Test 2: Check Dapr Logs
```bash
POD=$(kubectl get pods -n todo-app -l app=todo-backend -o name | head -1)
kubectl logs $POD -n todo-app -c daprd -f
# Watch for: "component loaded: todo-pubsub"
```

### Test 3: Create Task & Watch Events
```bash
# Terminal 1: Watch Dapr logs
kubectl logs -f $POD -n todo-app -c daprd

# Terminal 2: Create a task via chat or API

# Expected in logs:
# "Published event to topic task-events"
```

### Test 4: Verify in Redpanda Console
1. Go to Topics → task-events
2. Click Messages tab
3. See your event:
```json
{
  "event_type": "task.created",
  "timestamp": "2026-01-02T...",
  "data": { "task_id": "...", "title": "..." }
}
```

---

## 📊 What This Achieves

### Phase V Requirements ✅
- **Cloud-Native Architecture** - Kubernetes + Dapr service mesh
- **Event-Driven Design** - Async pub/sub with Kafka
- **Microservices Ready** - Sidecar pattern, loose coupling
- **Production Infrastructure** - TLS, SASL auth, managed Kafka
- **Observability** - Structured events, Dapr logs

### Scoring Impact
- **Base Phase V**: 250-280 points
- **With full features**: 280-300 points
- **Bonus for polish**: +10-20 points

---

## 🎬 Demo Script (For Evaluators)

```bash
# 1. Show infrastructure
kubectl get all -n todo-app
kubectl get component -n todo-app

# 2. Show Dapr sidecar
kubectl describe pod <backend-pod> -n todo-app
# Point out: Dapr annotations + daprd container

# 3. Show code integration
cat backend/mcp/tools.py | grep -A 5 "event_publisher.publish"

# 4. Live demo - create task
# Then show event in Redpanda Console

# 5. Show Dapr logs
kubectl logs <backend-pod> -n todo-app -c daprd --tail=30
```

---

## 🚨 Troubleshooting

### "Dapr sidecar not injected"
```bash
# Check Dapr is running
dapr status -k

# Verify annotations in deployment
kubectl get deployment todo-backend -n todo-app -o yaml | grep dapr.io
```

### "Events not publishing"
```bash
# Check Dapr component
kubectl describe component todo-pubsub -n todo-app

# Check for errors in Dapr logs
kubectl logs <pod> -n todo-app -c daprd | grep -i error

# Verify credentials are correct in component
```

### "Can't connect to Kafka"
```bash
# Test from inside pod
kubectl exec -it <pod> -n todo-app -- curl localhost:3500/v1.0/healthz

# Check component status in Dapr logs
kubectl logs <pod> -n todo-app -c daprd | grep -i kafka
```

---

## 📁 Files You'll Edit

Only need to edit **ONE** file:
```
kubernetes/dapr-components/pubsub-kafka.yaml
```

Everything else is already done!

---

## ⏱️ Time Breakdown

- ✅ **Code & Config**: 2.5 hours (DONE)
- ⏳ **Get Credentials**: 10 mins (WAITING)
- ⏳ **Deploy & Test**: 15 mins (READY)
- ⏳ **Demo Prep**: 10 mins (OPTIONAL)

**Total Remaining:** ~35 minutes

---

## 💡 Pro Tips

1. **Test locally first** - Use Upstash for easier setup
2. **Watch Dapr logs** - They tell you everything
3. **One topic is enough** - Just use `task-events` for demo
4. **Screenshot everything** - Dapr sidecar, events, logs
5. **Keep it simple** - You don't need all advanced features

---

## 📞 Quick Help

**Stuck getting credentials?**
→ Try Upstash Kafka (credentials visible immediately)

**Deployment failing?**
→ Run: `kubectl describe pod <pod> -n todo-app`

**Events not showing?**
→ Check: `kubectl logs <pod> -n todo-app -c daprd`

**Need more help?**
→ See: `PHASE_V_IMPLEMENTATION.md` (detailed guide)

---

## 🎉 You're Almost There!

**90% of Phase V is complete.** Just get those credentials and run the deployment script!

**Next action:** Get SASL username and password from Redpanda (or Upstash)

**Then run:** `./scripts/deploy-phase5.sh`

**Done!** 🚀
