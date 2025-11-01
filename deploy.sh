#!/bin/bash

# Smart Medicine Box AI - Automated Deployment Script
# This script rebuilds and redeploys your container app when you make changes

set -e  # Exit on any error

# Configuration
ACR_NAME="ecsairegistry2025"
RESOURCE_GROUP="ecs-ai-rg"
APP_NAME="ecs-ai-backend"
IMAGE_NAME="smart-medicine-box"

# Get current timestamp for versioning
VERSION=$(date +%Y%m%d-%H%M%S)
IMAGE_TAG="${IMAGE_NAME}:${VERSION}"
FULL_IMAGE_NAME="${ACR_NAME}.azurecr.io/${IMAGE_TAG}"

echo "🚀 Starting deployment of Smart Medicine Box AI..."
echo "📦 Image: ${FULL_IMAGE_NAME}"

# Step 1: Build Docker image
echo "🔨 Building Docker image..."
docker build -t ${IMAGE_TAG} .

# Step 2: Tag for ACR
echo "🏷️  Tagging image for Azure Container Registry..."
docker tag ${IMAGE_TAG} ${FULL_IMAGE_NAME}

# Step 3: Push to ACR
echo "📤 Pushing image to Azure Container Registry..."
docker push ${FULL_IMAGE_NAME}

# Step 4: Update Container App
echo "🔄 Updating Azure Container App..."
az containerapp update \
    --name ${APP_NAME} \
    --resource-group ${RESOURCE_GROUP} \
    --image ${FULL_IMAGE_NAME}

# Step 5: Wait for deployment
echo "⏳ Waiting for deployment to complete..."
sleep 30

# Step 6: Test the deployment
echo "🧪 Testing the deployment..."
APP_URL="https://ecs-ai-backend.livelycoast-b6426dc8.centralindia.azurecontainerapps.io"

# Test health endpoint
HEALTH_RESPONSE=$(curl -s ${APP_URL}/health || echo "ERROR")

if [[ $HEALTH_RESPONSE == *"healthy"* ]]; then
    echo "✅ Deployment successful! Your Smart Medicine Box AI is running."
    echo "🌐 API URL: ${APP_URL}"
    echo "📋 Health check: ${APP_URL}/health"
    echo "📋 API routes: ${APP_URL}/routes"
else
    echo "❌ Deployment might have issues. Please check the logs:"
    echo "   az containerapp logs show --name ${APP_NAME} --resource-group ${RESOURCE_GROUP}"
fi

echo "🎉 Deployment process completed!"