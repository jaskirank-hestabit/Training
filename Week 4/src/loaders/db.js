const mongoose = require("mongoose");
const config = require("../config");
const logger = require("../utils/logger");

async function connectDB() {
  try {
    logger.info("Connecting to database...");

    await mongoose.connect(config.mongoUri, {
      autoIndex: process.env.NODE_ENV !== "prod",
    });

    logger.info("Database connected");
  } catch (err) {
    logger.error("Database connection failed", err);
    process.exit(1);
  }
}

async function closeDB() {
  try {
    await mongoose.connection.close();
    logger.info("Database connection closed");
  } catch (err) {
    logger.error("Error closing database connection", err);
  }
}

module.exports = { connectDB, closeDB };
