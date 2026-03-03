// const accountRepository = require("../repositories/account.repository");
// const { sendEmailJob } = require("../jobs/email.job");

// class AccountService {
//   async createAccount(data) {
//     // Create account in DB
//     const account = await accountRepository.create(data);

//     // Trigger async email job
//     await sendEmailJob({
//       to: account.email,
//       subject: "Welcome to our platform",
//       name: account.fullName,
//     });

//     return account;
//   }

//   async getAccountById(id) {
//     return accountRepository.findById(id);
//   }

//   async getAccountsPaginated(options) {
//     return accountRepository.findPaginated(options);
//   }

//   async updateAccount(id, data) {
//     return accountRepository.update(id, data);
//   }

//   async deleteAccount(id) {
//     return accountRepository.delete(id);
//   }
// }

// module.exports = new AccountService();



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
}

module.exports = new AccountService();