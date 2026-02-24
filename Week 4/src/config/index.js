const dotenv = require("dotenv");
const path = require("path");

const env = process.env.NODE_ENV || "local";

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