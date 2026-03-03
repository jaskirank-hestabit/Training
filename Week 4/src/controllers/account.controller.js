const accountService = require("../services/account.service");
const logger = require("../utils/logger");

class AccountController {
  async createAccount(req, res, next) {
    try {
      const account = await accountService.createAccount(req.body);

      logger.info({
        requestId: req.requestId,
        event: "ACCOUNT_CREATED",
        accountId: account._id,
      });

      res.status(201).json({
        success: true,
        data: account,
      });
    } catch (err) {
      next(err);
    }
  }
}

module.exports = new AccountController();