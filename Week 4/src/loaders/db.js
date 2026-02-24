const { MongoClient } = require("mongodb");
const config = require("../config");
const logger = require("../utils/logger");

let client;

async function connectDB() {
  try {
    logger.info("Connecting to database...");

    client = new MongoClient(config.mongoUri);
    await client.connect();

    logger.info("Database connected");
  } catch (err) {
    logger.error("Database connection failed");
    process.exit(1);
  }
}

async function closeDB() {
  if (client) {
    await client.close();
    logger.info("Database connection closed");
  }
}

module.exports = { connectDB, closeDB };