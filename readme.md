# Training

This repository contains my work and learnings from the **Engineering Mindset Bootcamp**.  
Each week folder consists of tasks completed and it also contains sub-folders for each day

---

# Week 1 — Engineering Mindset Bootcamp

Week 1 focused on understanding systems, working with Node.js, building CLI tools, and developing strong Git fundamentals.

---

## Day 1 — System Reverse Engineering + Node & Terminal

The goal of Day 1 was to understand the system environment and get comfortable with Node.js and terminal usage.

### Work Done

- Created a Node.js script `sysinfo.js` that prints:
  - Hostname
  - Available disk space (GB)
  - Top 5 open ports
  - Default network gateway
  - Logged-in users count

- Created shell aliases and stored them in `.bashrc`:
  ```bash
  alias gs="git status"
  alias files="ls -lha"
  alias ports="lsof -i -P -n | grep LISTEN"
  ```
- Ran the Node script and captured runtime metrics using:
  ```js
  process.cpuUsage()
  process.resourceUsage()
  ```
Stored runtime metrics in: logs/day1-sysmetrics.json

### Deliverables
1) sysinfo.js
2) .bashrc alias snippet (screenshot)
3) logs/day1-sysmetrics.json

## Day 2 — Node CLI & Concurrency

Day 2 focused on building a CLI tool in Node.js and understanding concurrency and performance.

### Work Done
- Built a CLI tool stats.js supporting:
  --lines <file>
  --chars <file>
  --words <file>

- The tool:
Counts total lines, characters, and words
Processes three files in parallel
Outputs a performance report

- Bonus
Added an option to remove duplicate lines
Wrote cleaned/unique output files to:
**output/unique-<filename>.txt**

### Deliverables
1) stats.js
2) logs/performance-timestamp.json
3) Output files with uniqueness processing

## Day 3 — Git Mastery (Reset, Revert, Cherry-pick, Stash)

Day 3 focused on understanding Git through real-world workflows and debugging scenarios.

### Work Done
1) Created a repository with 10 commits

2) Introduced a syntax error in commit 5

3) Used git bisect to identify the breaking commit

4) Created a release branch from an older commit:
```bash
release/v0.1
```

5) Used git cherry-pick to move selected commits from main to the release branch

6) Demonstrated git stash usage:
 - Saved uncommitted changes
 - Switched branches safely
 - Restored changes cleanly

### Deliverables
1) bisect-log.txt
2) cherry-pick-report.md
3) stash-proof.txt
4) Commit graph screenshot

## Day 4 — HTTP / API Forensics (cURL + Postman)

Day 4 focused on understanding HTTP requests, APIs, and network-level behavior.

### Work Done
1) Used curl to fetch GitHub API data:
```bash
curl -v https://api.github.com/users/octocat
```
Extracted and logged:
Rate-limit remaining
ETag
Server header

2) Tested pagination:
```bash
https://api.github.com/users/octocat/repos?page=1&per_page=5
```
Documented link headers and page navigation

3) Created a Postman collection to test:
**GET** GitHub user
**GET** repositories across 3 pages

4) Built an HTTP server with:
**/ping** → returns timestamp
**/headers** → returns request headers
**/count** → maintains an in-memory counter

### Deliverables
1) curl-headers.txt
2) pagination-analysis.md
3) Exported Postman collection (.json)
4) server.js