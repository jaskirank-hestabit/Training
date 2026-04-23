const Order = require("../models/Order");

class OrderRepository {
  async create(data) {
    return await Order.create(data);
  }

  async findById(id) {
    return await Order.findById(id).populate("account");
  }

  async findPaginated({ page = 1, limit = 10, status }) {
    const skip = (page - 1) * limit;
    const query = status ? { status } : {};

    return await Order.find(query)
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(limit)
      .populate("account");
  }

  async update(id, data) {
    return await Order.findByIdAndUpdate(id, data, {
      new: true,
      runValidators: true,
    });
  }

  async delete(id) {
    return await Order.findByIdAndDelete(id);
  }
}

module.exports = new OrderRepository();