const express = require("express");
const cors = require("cors");
const logger = require("../utils/logger");
const requestLogger = require("../middlewares/requestLogger");
const requestTimer = require("../middlewares/requestTimer");
const routes = require("../routes");
const errorMiddleware = require("../middlewares/error.middleware");

function createApp() {
  const app = express();

  logger.info("Initializing Express...");

  // Built-in middlewares
  app.use(express.json());
  app.use(cors());

  // Custom middlewares
  app.use(requestLogger);
  app.use(requestTimer);
  
  logger.info("Middlewares loaded");
  
  app.use("/api", routes);

  app.use(errorMiddleware);

  logger.info("Routes mounted: 3 endpoints");

  return app;
}

module.exports = createApp;