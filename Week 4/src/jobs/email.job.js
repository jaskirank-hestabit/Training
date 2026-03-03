const { emailQueue } = require("./queue");

async function sendEmailJob(payload) {
  await emailQueue.add("sendEmail", payload, {
    attempts: 3,
    backoff: {
      type: "exponential",
      delay: 5000,
    },
  });
}

module.exports = { sendEmailJob };