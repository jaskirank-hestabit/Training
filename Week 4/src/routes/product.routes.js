// day 3

const express = require("express");
const router = express.Router();

const productController = require("../controllers/product.controller");

const validate = require("../middlewares/validate");

const {
  productQuerySchema,
  idParamSchema,
  createProductSchema,
} = require("../validations/product.schema");

// Validate query before hitting controller
router.get(
  "/",
  validate(productQuerySchema, "query"),
  productController.getProducts
);

// Validate ID param before delete
router.delete(
  "/:id",
  validate(idParamSchema, "params"),
  productController.deleteProduct
);

// To test payload whitelisting 
router.post(
  "/",
  validate(createProductSchema, "body"),
  productController.createProduct
);

module.exports = router;