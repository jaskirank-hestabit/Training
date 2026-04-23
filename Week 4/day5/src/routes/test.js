const express = require("express");
const router = express.Router();
const accountRepo = require("../repositories/account.repository");
const orderRepo = require("../repositories/order.repository");
router.get("/seed", async (req, res) => {
  try {
    const user = await accountRepo.create({
      firstName: "Jas",
      lastName: "Kaur",
      email: "jas" + Date.now() + "@test.com",
      password: "123456",
    });
    const order = await orderRepo.create({
      account: user._id,
      items: [
        { productName: "Laptop", price: 50000, quantity: 1 },
        { productName: "Mouse", price: 1000, quantity: 2 },
      ],
      totalAmount: 52000,
      status: "pending",
    });
    res.json({ account: user, order });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: err.message });
  }
});
module.exports = router;
