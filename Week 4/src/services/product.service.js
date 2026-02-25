// day 3

const productRepository = require("../repositories/product.repository");
const AppError = require("../utils/AppError");
const mongoose = require("mongoose");

class ProductService {
  async getProducts(queryParams) {
    const {
      search,
      minPrice,
      maxPrice,
      tags,
      sort,
      page = 1,
      limit = 10,
      includeDeleted,
    } = queryParams;

    const query = {};

    // Soft delete filter
    if (!includeDeleted) {
      query.deletedAt = null;
    }

    // Search (regex)
    if (search) {
      query.$or = [
        { name: { $regex: search, $options: "i" } },
        { description: { $regex: search, $options: "i" } },
      ];
    }

    // Price filtering
    if (minPrice || maxPrice) {
      query.price = {};
      if (minPrice) query.price.$gte = Number(minPrice);
      if (maxPrice) query.price.$lte = Number(maxPrice);
    }

    // Tags filter (AND logic)
    if (tags) {
      query.tags = { $all: tags.split(",") };
    }

    // Sorting
    let sortOption = {};
    if (sort) {
      const [field, order] = sort.split(":");
      sortOption[field] = order === "desc" ? -1 : 1;
    }

    const skip = (page - 1) * limit;

    const data = await productRepository.findWithFilters(query, {
      sort: sortOption,
      skip,
      limit: Number(limit),
    });

    const total = await productRepository.count(query);

    return {
      data,
      pagination: {
        total,
        page: Number(page),
        pages: Math.ceil(total / limit),
      },
    };
  }


async deleteProduct(id) {
  // Validate ID format first
  if (!mongoose.Types.ObjectId.isValid(id)) {
    throw new AppError("Invalid product ID", "INVALID_ID", 400);
  }

  const product = await productRepository.findById(id);

  if (!product) {
    throw new AppError("Product not found", "PRODUCT_NOT_FOUND", 404);
  }

  return productRepository.softDelete(id);
}
}

module.exports = new ProductService();
