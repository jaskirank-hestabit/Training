const { Queue } = require("bullmq");
const IORedis = require("ioredis");
const config = require("../config");

const connection = new IORedis(config.REDIS_URL, {
  maxRetriesPerRequest: null,
});

const emailQueue = new Queue("emailQueue", {
  connection,
});

module.exports = { emailQueue };