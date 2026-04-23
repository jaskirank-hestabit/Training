module.exports = (req, res, next) => {
  const start = Date.now();
  res.on("finish", () => {
    const duration = Date.now() - start;
    console.log(`Request processed in ${duration}ms`);
  });
  next();
};