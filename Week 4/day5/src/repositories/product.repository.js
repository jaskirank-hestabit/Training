// day 3

const Product = require("../models/Product");

class ProductRepository {
  async findWithFilters(query, options) {
    return Product.find(query)
      .sort(options.sort)
      .skip(options.skip)
      .limit(options.limit);
  }

  async count(query) {
    return Product.countDocuments(query);
  }

  async findById(id) {
    return Product.findById(id);
  }

  async create(data) {
    return Product.create(data);
  }
  
  async softDelete(id) {
    return Product.findByIdAndUpdate(id, {
      deletedAt: new Date(),
    });
  }
}

module.exports = new ProductRepository();