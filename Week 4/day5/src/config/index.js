const dotenv = require("dotenv");
const path = require("path");

const env = process.env.NODE_ENV || "local";
REDIS_URL: process.env.REDIS_URL || "redis://127.0.0.1:6379";

const envFile = {
  local: ".env.local",
  dev: ".env.dev",
  prod: ".env.prod",
}[env];

dotenv.config({ path: path.resolve(process.cwd(), envFile) });

if (!process.env.PORT || !process.env.MONGO_URI) {
  throw new Error("Missing required environment variables");
}

module.exports = {
  env,
  port: process.env.PORT,
  mongoUri: process.env.MONGO_URI,
  logLevel: process.env.LOG_LEVEL || "info",
};