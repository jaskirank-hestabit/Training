const Account = require("../models/Account");

class AccountRepository {
  async create(data) {
    return await Account.create(data);
  }

  async findById(id) {
    return await Account.findById(id);
  }

  async findPaginated({ page = 1, limit = 10, status }) {
    const skip = (page - 1) * limit;
    const query = status ? { status } : {};

    return await Account.find(query)
      .sort({ createdAt: -1 })
      .skip(skip)
      .limit(limit);
  }

  async update(id, data) {
    return await Account.findByIdAndUpdate(id, data, {
      new: true,
      runValidators: true,
    });
  }

  async delete(id) {
    return await Account.findByIdAndDelete(id);
  }
}

module.exports = new AccountRepository();