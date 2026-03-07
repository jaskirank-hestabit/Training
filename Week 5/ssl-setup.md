# SSL Setup with mkcert + NGINX

## Objective

Enable HTTPS for the Docker multi-container application using NGINX reverse proxy.

## Architecture
```text
Browser (HTTPS)
    |
NGINX Reverse Proxy (SSL termination)
    |
Node Backend Containers
    |
MongoDB
```

NGINX handles SSL termination and distributes traffic across multiple Node.js backend containers.

## Step 1 – Install mkcert

mkcert allows generating trusted local SSL certificates.

Install:
```bash
sudo apt install libnss3-tools
mkcert -install
```

## Step 2 – Local Domain

Add to /etc/hosts:
Command to edit host file : 
```bash
sudo nano /etc/hosts
```

Add: 
```bash 
127.0.0.1 docker.local
```

## Step 3 – Generate Certificate
```bash
mkcert docker.local
```

Generated files:

docker.local.pem
docker.local-key.pem

Stored inside:

nginx/certs/

## Step 4 – Configure NGINX

NGINX listens on:

8080 - HTTP (redirects to HTTPS)
8443 - HTTPS (SSL termination)

SSL termination occurs at NGINX.

## Step 5 – Start Containers

docker compose up --build

## Step 6 – Verify

Open:

https://docker.local:8443/api

Browser displays a lock icon indicating HTTPS connection.

Refreshing the page shows responses from different backend containers confirming load balancing.

## Project Ports
Service Ports

React Client     → http://localhost:3000
HTTP Proxy       → http://docker.local:8080
HTTPS Proxy      → https://docker.local:8443
API Endpoint     → https://docker.local:8443/api


## Screenshots

HTTPS Working -
![HTTPS-Working](./screenshots/day4/https-working.png)