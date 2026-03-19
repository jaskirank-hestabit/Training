# NGINX Reverse Proxy + Load Balancing

## Architecture

Client → NGINX → Backend Containers → MongoDB

NGINX acts as a reverse proxy that routes API requests to multiple backend servers.

## Backend Replicas

Two Node.js containers are running:

- server1
- server2

Both connect to the same MongoDB container using Docker networking.

## Reverse Proxy Routing

NGINX routes:

/api → backend_servers

## Load Balancing

NGINX upstream block:

upstream backend_servers {
    server server1:5000;
    server server2:5000;
}

NGINX uses **round-robin load balancing by default**, distributing requests across backend containers.

## Running the system

Start containers:

docker compose up --build

Access API:

http://localhost:8080/api

Refreshing the page shows responses from different containers, proving load balancing works.

## Screenshots 

1) Terminal logs - on loading and refreshing http://localhost:8080/api 
![logs](./screenshots/day3/terminal-logs.png)

2) Connected to node-server 1
![node-server1](./screenshots/day3/node-server1.png)

3) Connecting to node-server 2 - on refreshing we connect to another node server  
![node-server2](./screenshots/day3/node-server2.png)