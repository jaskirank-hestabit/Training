# Multi Container Architecture

This project uses Docker Compose to run a multi-container application.

Services:

1. Client (React)
- Runs frontend UI
- Port: 3000

2. Server (Node.js / Express)
- Handles API requests
- Connects to MongoDB
- Port: 5000

3. MongoDB
- Database service
- Port: 27017
- Uses Docker Volume for persistent storage

Networking:
Docker Compose automatically creates a bridge network allowing services to communicate using container names.

Example:
Server connects to Mongo using:
mongodb://mongo:27017/week5db

Volumes:
MongoDB uses a named volume:
mongo-data:/data/db

This ensures database persistence even when containers restart.

## Screenshots 
1) docker ps 
![docker ps](./screenshots/day2/docker-ps.png)

2) docker compose logs
![docker compose logs](./screenshots/day2/docker-compose-logs.png)

3) Networking 
![Networking - server to mongo ping](./screenshots/day2/server-mongo-networking.png)