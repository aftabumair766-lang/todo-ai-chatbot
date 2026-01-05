# Kafka/Redpanda Setup Guide - CRITICAL FIX

## Problem Identified

✅ **Connection**: Working
✅ **Authentication**: Working
✅ **Brokers**: All 3 visible
❌ **Topics**: 0 topics found - THIS IS THE ISSUE!

## Root Cause

The kcat test showed `0 topics` which means either:
1. Topics don't exist yet in Redpanda
2. User `prometheus` doesn't have permission to list/access topics
3. Topics were deleted

## SOLUTION: Create Topics in Redpanda Console

### Step 1: Login to Redpanda Cloud
https://cloud.redpanda.com

### Step 2: Select Your Cluster
Click on cluster: `d5bd76jrcoacstiscs80`

### Step 3: Create Topics

Go to **Topics** tab and create these 3 topics:

#### Topic 1: task-events
```
Name: task-events
Partitions: 3
Replication Factor: 3
Cleanup Policy: delete
Retention: 7 days (604800000 ms)
```

#### Topic 2: tag-events
```
Name: tag-events
Partitions: 1
Replication Factor: 3
Cleanup Policy: delete
Retention: 7 days (604800000 ms)
```

#### Topic 3: reminder-events
```
Name: reminder-events
Partitions: 1
Replication Factor: 3
Cleanup Policy: delete
Retention: 7 days (604800000 ms)
```

### Step 4: Verify ACL Permissions

Go to **Security** → **ACLs** and ensure user `prometheus` has these permissions:

**For ALL topics** (`*` or specific topics):
- ✅ READ
- ✅ WRITE
- ✅ CREATE
- ✅ DESCRIBE
- ✅ DESCRIBE_CONFIGS

**For consumer groups**:
- ✅ READ (on group `todo-chatbot-group`)

### Step 5: Test Connection After Creating Topics

```bash
# Run this command to test
kubectl run kafka-test-2 --rm -i --restart=Never --image=edenhill/kcat:1.7.1 -- \
  -b d5bd76jrcoacstiscs80.any.us-east-1.mpx.prd.cloud.redpanda.com:9092 \
  -X security.protocol=SASL_SSL \
  -X sasl.mechanism=SCRAM-SHA-256 \
  -X sasl.username=prometheus \
  -X sasl.password=F0we4PD0tJ927zub76bPTV5bh9G1JV \
  -L -t task-events
```

**Expected output:**
```
Metadata for task-events:
 3 brokers:
  broker 13 at ...
  broker 14 at ...
  broker 15 at ...
 1 topics:
  topic "task-events" with 3 partitions:  ← YOU SHOULD SEE THIS!
    partition 0, leader 13, replicas: 13,14,15
    partition 1, leader 14, replicas: 14,15,13
    partition 2, leader 15, replicas: 15,13,14
```

## Alternative: Use Redpanda Console UI to Verify

After creating topics:
1. Go to **Topics** tab
2. You should see: `task-events`, `tag-events`, `reminder-events`
3. Click on `task-events` → Check if partitions are shown
4. Try **producing a test message** using Console's built-in producer

## Why This Fixes the Issue

When Dapr's Kafka component initializes, it calls the Kafka API to:
1. **Discover brokers** ✅ (this works)
2. **List topics** ❌ (fails because 0 topics exist/visible)
3. **Create producer/consumer** ❌ (can't proceed without topics)

Once topics exist and are visible, Dapr will successfully initialize!

## After Creating Topics - Deploy Dapr Component

Once topics are created and visible, run:

```bash
# Apply Kafka component
kubectl apply -f kubernetes/dapr-components/pubsub-kafka.yaml

# Restart deployment to reload component
kubectl rollout restart deployment/todo-backend -n todo-app

# Watch pod status (should be 2/2 Running)
kubectl get pods -n todo-app -l app=todo-backend -w

# Check Dapr logs for success
kubectl logs -n todo-app <pod-name> -c daprd | grep -i "component loaded"
# Should see: "component loaded. name: todo-pubsub (pubsub.kafka/v1)"
```

## Verification Checklist

- [ ] Topics created in Redpanda Console
- [ ] ACL permissions verified for user `prometheus`
- [ ] kcat can list topics (shows 3 topics, not 0)
- [ ] kcat can produce message to `task-events`
- [ ] Dapr component applied
- [ ] Pod shows 2/2 Running
- [ ] Dapr logs show "component loaded: todo-pubsub"
- [ ] Create a task and see event in Redpanda Console

---

## Current Credentials (Confirmed Working)

```
Bootstrap Server: d5bd76jrcoacstiscs80.any.us-east-1.mpx.prd.cloud.redpanda.com:9092
Username: prometheus
Password: F0we4PD0tJ927zub76bPTV5bh9G1JV
SASL Mechanism: SCRAM-SHA-256
Security Protocol: SASL_SSL
```

**Connection Test**: ✅ SUCCESSFUL (3 brokers discovered)
**Topics Visible**: ❌ 0 topics (NEEDS FIX)

---

## Next Step

**ACTION REQUIRED**:
1. Login to Redpanda Console
2. Create the 3 topics listed above
3. Verify ACL permissions
4. Run the test command to confirm topics are visible
5. Then we'll deploy Dapr component

**Estimated Time**: 5-10 minutes

Once done, tell me "topics create kar diye" and I'll deploy the Dapr component!
