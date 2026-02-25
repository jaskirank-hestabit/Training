// day 3

const express = require("express");
const router = express.Router();
const productController = require("../controllers/product.controller");

router.get("/", productController.getProducts);
router.delete("/:id", productController.deleteProduct);

module.exports = router;