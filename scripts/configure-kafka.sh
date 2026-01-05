#!/bin/bash
# Configure Kafka component from .env credentials

set -e

# Source the .env file to get credentials
export $(grep -E "KAFKA_BOOTSTRAP_SERVERS|user_name|password" backend/.env | xargs)

# Create the Kafka component YAML
cat > kubernetes/dapr-components/pubsub-kafka.yaml <<EOF
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: todo-pubsub
  namespace: todo-app
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "${KAFKA_BOOTSTRAP_SERVERS}"
  - name: consumerGroup
    value: "todo-chatbot-group"
  - name: authType
    value: "password"
  - name: saslUsername
    value: "${user_name}"
  - name: saslPassword
    value: "${password}"
  - name: saslMechanism
    value: "SCRAM-SHA-256"
  - name: enableTLS
    value: "true"
EOF

echo "✅ Kafka component configured at: kubernetes/dapr-components/pubsub-kafka.yaml"
echo "✅ Bootstrap: ${KAFKA_BOOTSTRAP_SERVERS}"
echo "✅ Username: ${user_name}"
echo "✅ Ready to deploy!"
