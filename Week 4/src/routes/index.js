const express = require("express");
const router = express.Router();

if (process.env.NODE_ENV === "dev") {
  const testRoutes = require("./test");
  router.use(testRoutes);
}

router.get("/health", (req, res) => {
  res.json({ status: "OK" });
});

router.get("/ping", (req, res) => {
  res.json({ message: "pong" });
});

module.exports = router;