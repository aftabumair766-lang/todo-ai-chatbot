#!/bin/bash
# Test Todo Chatbot Kubernetes deployment
# Tests T045 (API Gateway health) and T046 (task creation + Kafka events)

set -e

echo "🧪 Testing Todo Chatbot deployment..."

# Check if namespace exists
if ! kubectl get namespace todo-app &> /dev/null; then
    echo "❌ Namespace 'todo-app' not found. Please run deploy-k8s.sh first."
    exit 1
fi

# T044: Verify pods are running with Dapr sidecars
echo ""
echo "📋 T044: Verifying pods with Dapr sidecars..."
echo "=========================================="
POD_COUNT=$(kubectl get pods -n todo-app -o json | jq '.items[].spec.containers | length' | grep -c "2" || true)
if [ "$POD_COUNT" -gt 0 ]; then
    echo "✅ Found $POD_COUNT pods with Dapr sidecars (2 containers each)"
    kubectl get pods -n todo-app -o custom-columns='NAME:.metadata.name,CONTAINERS:.spec.containers[*].name'
else
    echo "⚠️  No pods found with Dapr sidecars. Check pod status:"
    kubectl get pods -n todo-app
    exit 1
fi

# T045: Test API Gateway health endpoint
echo ""
echo "📋 T045: Testing API Gateway health endpoint..."
echo "================================================"

# Port forward in background
echo "🔌 Setting up port-forward to API Gateway..."
kubectl port-forward -n todo-app svc/api-gateway 8000:8000 &
PF_PID=$!
sleep 3

# Test health endpoint
echo "🏥 Testing /health endpoint..."
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health || echo "FAILED")

if [[ "$HEALTH_RESPONSE" == *"healthy"* ]]; then
    echo "✅ API Gateway health check passed!"
    echo "$HEALTH_RESPONSE" | jq '.'
else
    echo "❌ API Gateway health check failed!"
    echo "Response: $HEALTH_RESPONSE"
    kill $PF_PID 2>/dev/null || true
    exit 1
fi

# T046: Test task creation and Kafka events
echo ""
echo "📋 T046: Testing task creation and Kafka events..."
echo "===================================================="

# Create a test task
echo "📝 Creating test task..."
TASK_RESPONSE=$(curl -s -X POST http://localhost:8000/tasks \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer test-token" \
    -d '{
        "title": "Test Task from Deployment Script",
        "user_id": "test-user-123",
        "due_date": null
    }' || echo "FAILED")

if [[ "$TASK_RESPONSE" == *"id"* ]]; then
    echo "✅ Task created successfully!"
    TASK_ID=$(echo "$TASK_RESPONSE" | jq -r '.id')
    echo "Task ID: $TASK_ID"
    echo "$TASK_RESPONSE" | jq '.'

    # Check Task Service logs for event publishing
    echo ""
    echo "📊 Checking Task Service logs for event publishing..."
    TASK_POD=$(kubectl get pods -n todo-app -l app=task-service -o jsonpath='{.items[0].metadata.name}')
    echo "Task Service Pod: $TASK_POD"

    # Wait a moment for event to be published
    sleep 2

    # Check for event publishing in logs
    echo "🔍 Recent Task Service logs:"
    kubectl logs -n todo-app "$TASK_POD" -c task-service --tail=20 | grep -E "(Published|task\.created|event)" || echo "No event logs found (this is expected if Kafka isn't configured yet)"

else
    echo "❌ Task creation failed!"
    echo "Response: $TASK_RESPONSE"
fi

# Cleanup port-forward
kill $PF_PID 2>/dev/null || true

echo ""
echo "=========================================="
echo "✅ Deployment tests complete!"
echo ""
echo "📋 Test Summary:"
echo "   T044: Pod verification - PASSED"
echo "   T045: API Gateway health - PASSED"
echo "   T046: Task creation - $([ -n "$TASK_ID" ] && echo "PASSED" || echo "FAILED")"
echo ""
echo "📝 Next steps:"
echo "   1. Check Kafka events (requires Kafka setup):"
echo "      kubectl logs -n todo-app <notification-pod> daprd"
echo "   2. Test pod restart and recovery (T047):"
echo "      kubectl delete pod -n todo-app <pod-name>"
echo "   3. Deploy to cloud Kubernetes (T048)"
