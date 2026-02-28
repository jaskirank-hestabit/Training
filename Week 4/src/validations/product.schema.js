// const Joi = require("joi");

// exports.createProductSchema = Joi.object({
//   name: Joi.string().trim().min(3).max(100).required(),
//   description: Joi.string().max(500).optional(),
//   price: Joi.number().min(0).required(),
//   tags: Joi.array().items(Joi.string()).optional(),
// });



const Joi = require("joi");

exports.productQuerySchema = Joi.object({
  search: Joi.string().optional(),

  minPrice: Joi.number().min(0).optional(),
  maxPrice: Joi.number().min(0).optional(),

  tags: Joi.string().optional(), // because you split by comma

  sort: Joi.string()
    .pattern(/^[a-zA-Z]+:(asc|desc)$/)
    .optional(),

  page: Joi.number().min(1).default(1),

  limit: Joi.number().min(1).max(100).default(10),

  includeDeleted: Joi.boolean().optional(),
});

exports.idParamSchema = Joi.object({
  id: Joi.string().length(24).hex().required(),
});

exports.createProductSchema = Joi.object({
  name: Joi.string().min(2).max(100).required(),
  description: Joi.string().max(500).optional(),
  price: Joi.number().min(0).required(),
  tags: Joi.array().items(Joi.string()).optional()
});