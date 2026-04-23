#!/bin/bash
set -e

echo "🚀 Starting Rolling Update Deployment..."

IMAGE_NAME="localhost:5000/api"
CONTAINER_NAME="api-prod"
HEALTH_URL="http://localhost:8000/health"
TIMEOUT=60

echo "Pulling latest image..."
docker pull $IMAGE_NAME:latest || true

echo "Starting new container on port 8001..."
docker run -d --name "api-new" \
  -p 8001:8000 \
  -e REDIS_HOST=redis \
  -e REDIS_PORT=6379 \
  $IMAGE_NAME:latest || {
    echo "Failed to start new container"
    exit 1
  }

echo "Waiting for health check (max ${TIMEOUT}s)..."
for i in $(seq 1 $((TIMEOUT/5))); do
  if curl -s -f http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ New container is healthy!"
    
    # Stop old container
    docker stop $CONTAINER_NAME 2>/dev/null || true
    docker rm $CONTAINER_NAME 2>/dev/null || true
    
    # Stop new container and restart on correct port
    docker stop api-new
    docker rm api-new
    
    docker run -d --name $CONTAINER_NAME \
      -p 8000:8000 \
      -e REDIS_HOST=redis \
      -e REDIS_PORT=6379 \
      $IMAGE_NAME:latest
    
    echo "✅ Deployment successful!"
    exit 0
  fi
  sleep 5
done

echo "❌ Health check failed. Rolling back..."
docker stop api-new 2>/dev/null || true
docker rm api-new 2>/dev/null || true
exit 1
