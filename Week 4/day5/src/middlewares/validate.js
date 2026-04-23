const AppError = require("../utils/AppError");

module.exports = (schema, property = "body") => {
  return (req, res, next) => {
    const { error, value } = schema.validate(req[property], {
      abortEarly: false,
      stripUnknown: true,
    });

    if (error) {
      const message = error.details.map((d) => d.message).join(", ");
      return next(new AppError(message, "VALIDATION_ERROR", 400));
    }

    // Instead of overwriting req.query / req.params
    Object.assign(req[property], value);

    next();
  };
};