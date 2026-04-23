const express = require("express");
const router = express.Router();

const accountRoutes = require("./account.routes");
const productRoutes = require("./product.routes");

// Dev-only routes
if (process.env.NODE_ENV === "dev") {
  const testRoutes = require("./test");
  router.use(testRoutes);
}

// Health routes
router.get("/health", (req, res) => {
  res.json({ status: "OK" });
});

router.get("/ping", (req, res) => {
  res.json({ message: "pong" });
});

// Account routes 
router.use("/accounts", accountRoutes);

// Product routes
router.use("/products", productRoutes);

module.exports = router;