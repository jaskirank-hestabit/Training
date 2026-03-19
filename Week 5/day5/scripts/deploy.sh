#!/bin/bash

echo "Stopping old containers..."

docker compose --profile prod -f docker-compose.prod.yml down

echo "Building images..."

docker compose --profile prod -f docker-compose.prod.yml build

echo "Starting containers..."

docker compose --profile prod -f docker-compose.prod.yml up -d

echo "Deployment complete!"