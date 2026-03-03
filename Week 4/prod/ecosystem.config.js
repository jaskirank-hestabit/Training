// Uses PM2
module.exports = {
  apps: [
    {
      name: "backend-api",
      script: "src/server.js",
      instances: "max",
      exec_mode: "cluster",
      env: {
        NODE_ENV: "prod"
      }
    },
    {
      name: "email-worker",
      script: "src/jobs/email.worker.js",
      instances: 1,
      exec_mode: "fork",
      env: {
        NODE_ENV: "prod"
      }
    }
  ]
};