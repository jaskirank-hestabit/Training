const accountRepository = require("../repositories/account.repository");
const { sendEmailJob } = require("../jobs/email.job");

class AccountService {
  async createAccount(data) {
    const account = await accountRepository.create(data);

    await sendEmailJob({
      to: account.email,
      subject: "Welcome to our platform",
      name: account.fullName,
    });

    return account;
  }

  async getAccountById(id) {
    const account = await accountRepository.findById(id);

    if (!account) {
      throw new Error("Account not found");
    }

    return account;
  }

  async getAccountsPaginated(options) {
    return await accountRepository.findPaginated(options);
  }

  async updateAccount(id, data) {
    const account = await accountRepository.update(id, data);

    if (!account) {
      throw new Error("Account not found");
    }

    return account;
  }

  async deleteAccount(id) {
    const account = await accountRepository.delete(id);

    if (!account) {
      throw new Error("Account not found");
    }

    return account;
  }
}

module.exports = new AccountService();