const logger = require("../utils/logger");

module.exports = (req, res, next) => {
  logger.info(`Incoming Request: ${req.method} ${req.url}`);
  next();
};