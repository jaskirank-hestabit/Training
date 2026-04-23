const winston = require("winston");
const config = require("../config");
const path = require("path");

const logger = winston.createLogger({
  level: config.logLevel,
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({
      filename: path.join("src/logs/app.log"),
    }),
  ],
});

module.exports = logger;