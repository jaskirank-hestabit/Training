const os = require("os");
const { execSync } = require("child_process");
const fs = require("fs");

// Helper to safely run shell commands
function run(cmd) {
  try {
    return execSync(cmd, { encoding: "utf8" }).trim();
  } catch {
    return "N/A";
  }
}

// hostname
const hostname = os.hostname();

// Available Disk Space (GB) 
let diskGB = "N/A";
try {
  const df = run("df -k /").split("\n")[1].split(/\s+/);
  const availableKB = parseInt(df[3], 10);
  diskGB = (availableKB / (1024 * 1024)).toFixed(2);
} catch {}

// Open Ports
let openPorts = "N/A";
try {
  openPorts = run("ss -tuln | head -n 6");
} catch {
  openPorts = "Ports info not available";
}

// default Gateway
const defaultGateway = run("ip route | grep default | awk '{print $3}'") ||
                       run("route -n | grep '^0.0.0.0' | awk '{print $2}'");

// Logged-in users count
let loggedInUsers = "N/A";
try {
  const users = run("who | wc -l");
  loggedInUsers = parseInt(users, 10);
} catch {}

// outputs
console.log(`Hostname: ${hostname}`);
console.log(`Available Disk Space: ${diskGB} GB`);
console.log("Open Ports (top 5):");
console.log(openPorts);
console.log(`Default Gateway: ${defaultGateway}`);
console.log(`Logged-in Users Count: ${loggedInUsers}`);
