# Backend Bootstrapping & Lifecycle
This backend follows a controlled startup sequence to ensure all dependencies are initialized in the correct order before the server begins accepting requests.

1. Startup Flow

The application starts from server.js, which acts as the system orchestrator.

Startup order:
 - server.js (Entry point)
 - Load environment configuration
 - Initialize logger
 - Establish database connection
 - Create Express application
 - Register middlewares
 - Mount routes
 - Start HTTP server (app.listen)

Each step depends on the successful completion of the previous one.

2. Dependency Orchestration

 - The server starts listening only after a successful database connection.
 - If configuration is invalid or the database fails to connect, the process exits immediately
 - This ensures the application never runs in a partially initialized state.

3. Environment-Based Configuration

The system supports multiple environments:
 - .env.local
 - .env.dev
 - .env.prod

The active environment is selected using the NODE_ENV variable.

Each environment can define:
 - Different ports
 - Different database URIs
- Different logging levels

This enables safe development and production deployment.

4. Logging Strategy

Logging is initialized before any major service.

The system logs:
 - Environment mode
 - Database connection status
 - Middleware initialization
 - Routes mounted
 - Server start confirmation

Logs are written to both console and file.

5. Graceful Shutdown

The application handles termination signals (SIGINT, SIGTERM) and performs:

  1. Stop accepting new requests
  2. Close database connection
  3. Log shutdown completion
  4. Exit process cleanly

This prevents abrupt termination and ensures system stability.

--- 

## Summary

The backend follows a production-style lifecycle:

Configuration -> Logging -> Database -> Express Setup -> Middlewares -> Routes -> Server Start -> Graceful Shutdown

This ensures reliability, maintainability, and controlled system behavior.