module.exports = function sanitizeMiddleware(req, res, next) {
  const sanitize = (obj) => {
    if (!obj || typeof obj !== "object") return;

    for (let key in obj) {
      if (key.startsWith("$") || key.includes(".")) {
        delete obj[key];
      } else if (typeof obj[key] === "object") {
        sanitize(obj[key]);
      }
    }
  };

  sanitize(req.body);
  sanitize(req.query);
  sanitize(req.params);

  next();
};