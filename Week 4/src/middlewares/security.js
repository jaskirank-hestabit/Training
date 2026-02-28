const express = require("express");
const helmet = require("helmet");
const cors = require("cors");
const rateLimit = require("express-rate-limit");
const sanitizeMiddleware = require("./sanitize");
const hpp = require("hpp");
const xss = require("xss-clean");
// const mongoSanitize = require("express-mongo-sanitize");

module.exports = function securityMiddleware(app) {
  // Helmet (secure headers)
  app.use(helmet());

  // CORS policy
  app.use(
    cors({
      origin: ["http://localhost:3000"], // Frontend which will send request
      methods: ["GET", "POST", "PUT", "DELETE"],
      credentials: true,
    }),
  );

  // Rate limiting
  const limiter = rateLimit({
    max: 100,
    windowMs: 15 * 60 * 1000,
    message: {
      success: false,
      message: "Too many requests, try again later",
      code: "RATE_LIMIT_EXCEEDED",
    },
  });

  app.use("/api", limiter);

  // Payload size limit (attack surface reduction)
  app.use(express.json({ limit: "10kb" }));

  // NoSQL injection protection
  //   app.use(mongoSanitize());     // they(mongosanitize, xss) give internal server error instead of validation error

  // XSS protection
    app.use(xss());

  // Custom NoSQL injection protection
  app.use(sanitizeMiddleware);

  // Prevent parameter pollution
  app.use(hpp());
};
