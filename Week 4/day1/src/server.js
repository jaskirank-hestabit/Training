const config = require("./config");
const logger = require("./utils/logger");
const { connectDB, closeDB } = require("./loaders/db");
const createApp = require("./loaders/app");

async function startServer() {
  try {
    logger.info(`Booting in ${config.env.toUpperCase()} mode`);

    await connectDB();

    const app = createApp();

    const server = app.listen(config.port, () => {
      logger.info(`Server started on port ${config.port}`);
    });

    // Graceful Shutdown
    const shutdown = async () => {
      logger.info("Shutting down...");

      server.close(async () => {
        await closeDB();
        logger.info("Shutdown complete");
        process.exit(0);
      });
    };

    process.on("SIGINT", shutdown);
    process.on("SIGTERM", shutdown);

  } catch (err) {
    logger.error("Startup failed");
    process.exit(1);
  }
}

startServer();