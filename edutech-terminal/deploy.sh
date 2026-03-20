#!/bin/bash

# --- deploy.sh ---

set -e

echo "🚀 Deploying EduTech Terminal Platform..."

# Create namespace
echo "📦 Creating namespace..."
kubectl apply -f k8s/namespace.yaml

# Create secrets
echo "🔐 Creating secrets..."
kubectl apply -f k8s/secrets.yaml

# Deploy backend
echo "🖥️  Deploying backend..."
kubectl apply -f k8s/backend-deployment.yaml

# Deploy frontend
echo "🌐 Deploying frontend..."
kubectl apply -f k8s/frontend-deployment.yaml

# Apply network policies
echo "🔒 Applying network policies..."
kubectl apply -f k8s/network-policy.yaml

# Apply resource quotas
echo "📊 Applying resource quotas..."
kubectl apply -f k8s/resource-quota.yaml

# Apply HPA
echo "📈 Applying autoscaling..."
kubectl apply -f k8s/hpa.yaml

# Apply ingress
echo "🌍 Applying ingress..."
kubectl apply -f k8s/ingress.yaml

echo "✅ Deployment complete!"
echo ""
echo "Check status with:"
echo "  kubectl get pods -n edutech-terminal"
echo "  kubectl get svc -n edutech-terminal"
echo ""
echo "Access the application at: https://edutech.example.com"