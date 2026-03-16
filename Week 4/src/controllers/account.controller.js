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

  async getAccount(req, res, next) {
    try {
      const account = await accountService.getAccountById(req.params.id);

      res.json({
        success: true,
        data: account,
      });
    } catch (err) {
      next(err);
    }
  }

  async getAccounts(req, res, next) {
    try {
      const { page, limit, status } = req.query;

      const accounts = await accountService.getAccountsPaginated({
        page,
        limit,
        status,
      });

      res.json({
        success: true,
        data: accounts,
      });
    } catch (err) {
      next(err);
    }
  }

  async updateAccount(req, res, next) {
    try {
      const account = await accountService.updateAccount(
        req.params.id,
        req.body
      );

      res.json({
        success: true,
        data: account,
      });
    } catch (err) {
      next(err);
    }
  }

  async deleteAccount(req, res, next) {
    try {
      await accountService.deleteAccount(req.params.id);

      res.json({
        success: true,
        message: "Account deleted successfully",
      });
    } catch (err) {
      next(err);
    }
  }
}

module.exports = new AccountController();