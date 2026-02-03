const fs = require("fs");
const path = require("path");

// CPU usage
const cpuUsage = process.cpuUsage();

// Resource usage
const resourceUsage = process.resourceUsage();

const metrics = {
  timestamp: new Date().toISOString(),
  cpuUsage,
  resourceUsage
};

const logsDir = path.join(__dirname, "logs");
if (!fs.existsSync(logsDir)) {
  fs.mkdirSync(logsDir);
}

// Writing data to JSON file
const logFile = path.join(logsDir, "day1-sysmetrics.json");
fs.writeFileSync(logFile, JSON.stringify(metrics, null, 2));

console.log("System metrics saved to logs/day1-sysmetrics.json");