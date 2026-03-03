const { Worker } = require("bullmq");
const IORedis = require("ioredis");
const config = require("../config");
const logger = require("../utils/logger");

const connection = new IORedis(config.REDIS_URL, {
  maxRetriesPerRequest: null,
});

const worker = new Worker(
  "emailQueue",
  async job => {
    logger.info({
      event: "EMAIL_JOB_STARTED",
      jobId: job.id,
      data: job.data,
    });

    // Simulate email sending
    await new Promise(resolve => setTimeout(resolve, 2000));

    logger.info({
      event: "EMAIL_JOB_COMPLETED",
      jobId: job.id,
    });
  },
  { connection }
);

worker.on("failed", (job, err) => {
  logger.error({
    event: "EMAIL_JOB_FAILED",
    jobId: job.id,
    error: err.message,
  });
});