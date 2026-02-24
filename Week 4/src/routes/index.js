const express = require("express");
const router = express.Router();

router.get("/health", (req, res) => {
  res.json({ status: "OK" });
});

router.get("/ping", (req, res) => {
  res.json({ message: "pong" });
});

module.exports = router;