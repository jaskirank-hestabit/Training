# Week 5 — Day 1  
## Docker Fundamentals + Linux Internals

# Objective

- Understand Docker images and containers  
- Run a Node.js application inside a container  
- Explore Linux environment inside container  
- Inspect processes, users, logs, and disk usage  
- Understand container lifecycle  

# Docker Image Build

From root `week-5` directory:

```bash
docker build -t week5-server ./server
```

Verify Image creation:
```bash
docker images
```

## Working Directory
/app

## Run Container 

Run container in detached mode:
```bash
docker run -d -p 5000:5000 --name week5-container week5-server
```

Check running containers:
```bash
docker ps
```

Test in browser:
http://localhost:5000

## Enter Container (Like SSH)
```bash
docker exec -it week5-container /bin/sh
```
This opens a shell inside the container.

## Files Observed
- server.js
- package.json
- package-lock.json
- node_modules/

## Running User
Checked using whoami

## Running Processes
Observed node server.js using ps

## Memory & CPU
Checked using top

## Disk Usage
Used df -h and du -sh /app

## Logs
Viewed using docker logs week5-container

## Observations
- Container runs minimal Alpine Linux
- Node runs as main process (PID 1)
- Filesystem is isolated
- Logs accessible from host

## Exit container
```bash
exit
```

## Stop & Remove Container

Stop container:
```bash
docker stop week5-container
```

Remove container:
```bash
docker rm week5-container
```

## Container Base Image
node:20-alpine

## Screenshots 
Exploring ls, ps, top, disk usage, logs

1) Commands - pwd, ls, whoami, id 
![Commands](./screenshots/day1/commands.png)

2) Cpu Usage
![Cpu Uage](./screenshots/day1/cpu-memory.png)

3) Disk Usage
![Disk Usage](./screenshots/day1/disk-usage.png)