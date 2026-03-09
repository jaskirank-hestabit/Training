# Production Deployment Guide

## Architecture

React Client → NGINX Reverse Proxy → Node Backend → MongoDB

## Environment Variables

Create a `.env` file:

NODE_ENV=production
PORT=5000
MONGO_URI=mongodb://mongo:27017/dockerdb
CLIENT_URL=https://docker.local:8443

## Deploy Application
Production :
Run:
```bash
./scripts/deploy.sh
```
or
```bash
docker compose --profile prod -f docker-compose.prod.yml up -d
```
Frontend: https://docker.local:8443

Development:
Uses volumes + hot reload.
```bash
docker compose up
```
Frontend: http://localhost:3000

## Health Monitoring

Backend exposes:

GET /health

Docker monitors container health using healthchecks.

## Log Rotation

Docker logs configured with:

max-size: 10m
max-file: 3

## Persistent Storage

MongoDB data stored in Docker volume:

mongo-data