const fs = require("fs/promises");
const path = require("path");
const { performance } = require("perf_hooks");

const args = process.argv.slice(2);

function parseArgs(args) {
  const tasks = [];
  for (let i = 0; i < args.length; i += 2) {
    tasks.push({ flag: args[i], file: args[i + 1] });
  }
  return tasks;
}

function countStats(text, flag) {
  if (flag === "--chars") return text.length;
  if (flag === "--lines") return text.split("\n").length;
  if (flag === "--words") return text.trim().split(/\s+/).length;
}

async function processFile({ flag, file }) {
  const startTime = performance.now();
  const startMem = process.memoryUsage().heapUsed;

  const content = await fs.readFile(file, "utf-8");
  const result = countStats(content, flag);

  const endTime = performance.now();
  const endMem = process.memoryUsage().heapUsed;

  return {
    file,
    flag,
    result,
    executionTimeMs: +(endTime - startTime).toFixed(2),
    memoryMB: +((endMem - startMem) / 1024 / 1024).toFixed(2)
  };
}

async function removeDuplicateLines(file) {
  const content = await fs.readFile(file, "utf-8");
  const unique = [...new Set(content.split("\n"))].join("\n");

  await fs.mkdir("output", { recursive: true });
  const outFile = path.join("output", `unique-${path.basename(file)}`);
  await fs.writeFile(outFile, unique);

  console.log(`Unique lines written to ${outFile}`);
}

async function main() {
  // bonus 
  if (args.includes("--unique")) {
    const file = args[args.indexOf("--unique") + 1];
    await removeDuplicateLines(file);

    // Remove --unique and filename so stats logic doesn't break
    args.splice(args.indexOf("--unique"), 2);
  }

  // Normal stats flow
  const tasks = parseArgs(args);

  // for unique we do not need performance logs
  if (tasks.length === 0) {
    return; // No stats requested, then no performance log
  }

  const results = await Promise.all(
    tasks.map(task => processFile(task))
  );

  console.log("Results:");
  results.forEach(r =>
    console.log(`${r.file} (${r.flag}): ${r.result}`)
  );

  await fs.mkdir("logs", { recursive: true });

  const logFile = `logs/performance-${Date.now()}.json`;
  await fs.writeFile(logFile, JSON.stringify(results, null, 2));

  console.log(`Performance logged to ${logFile}`);
}

main();
