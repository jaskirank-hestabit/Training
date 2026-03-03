# Deployment Notes – Async Workers Backend

## Overview

This project implements a production-ready backend system with:

- Layered architecture (Controller → Service → Repository)
- Async background jobs using BullMQ + Redis
- Structured logging using Winston
- Request tracing using X-Request-ID
- Centralized error handling
- Security hardening (Helmet, CORS, Rate limiting)
- PM2 process management for production

---

# 1. System Requirements

- Node.js v18+
- MongoDB running
- Redis server running
- PM2 (for production process management)

Install PM2 globally:

npm install -g pm2

---

# 2. Environment Configuration

Environment files supported:

- .env.local
- .env.dev
- .env.prod

Example production configuration:
NODE_ENV=prod
PORT=3000
MONGO_URI=mongodb://localhost:27017/prodDB
REDIS_URL=redis://127.0.0.1:6379
LOG_LEVEL=info


Copy example file:

cp prod/.env.example

Important:
Environment files are not committed to version control.

---

# 3. Running in Development Mode

Open 3 terminals:

Terminal 1 – Start Redis

sudo service redis-server start

Terminal 2 – Start API server

npm run dev

Terminal 3 – Start Email Worker

NODE_ENV=dev node src/jobs/email.worker.js

---

# 4. Background Job Architecture

- Queue system: BullMQ
- Redis used as message broker
- Worker runs as separate process
- Retry mechanism enabled
- Backoff strategy applied
- Logs generated for:
  - Job started
  - Job completed
  - Job failure (if any)

Account creation triggers async email job.

---

# 5. Request Tracing & Observability

Every request:

- Receives X-Request-ID header
- Auto-generates UUID if not provided
- Logs grouped by requestId
- Execution time logged
- Logs stored in:

src/logs/app.log

Structured JSON logging format used.

---

# 6. Production Deployment (PM2)

Production config located at:

prod/ecosystem.config.js

Start production processes:

pm2 start prod/ecosystem.config.js

This starts:

1. backend-api (cluster mode, max instances)
2. email-worker (fork mode, single instance)

To check status:

pm2 status

To view logs:

pm2 logs

To stop:

pm2 stop all

---

# 7. Graceful Shutdown

Application listens for:

- SIGINT
- SIGTERM

On shutdown:
- Stops accepting new connections
- Closes database connection
- Exits cleanly

---

# 8. Logging Strategy

- Console logs enabled
- File logging enabled (Winston)
- Logs stored in:

src/logs/app.log

In production, logs can be forwarded to:

- ELK Stack
- Datadog
- Cloud logging providers

---

# 9. Security Controls Enabled

- Helmet headers
- CORS policy
- Rate limiting
- Payload size limits
- NoSQL injection protection
- XSS sanitization
- Parameter pollution protection

---

# 10. Deployment Checklist

Before deploying:

- Ensure Redis is running
- Ensure MongoDB is running
- Set NODE_ENV=prod
- Configure .env.prod correctly
- Start using PM2
- Verify logs are being written
- Test health endpoint:

GET /api/health

---

Deployment complete.