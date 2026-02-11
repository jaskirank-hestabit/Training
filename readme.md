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


## Day 5 — Automation & Mini-CI Pipeline

Day 5 focused on basic automation, validation before commits, and task scheduling — simulating a lightweight CI workflow.

### Work Done

- Built a shell script `healthcheck.sh` to perform server health checks:
  - Pings a target server once per execution
  - Logs failures to `logs/health.log`
  - Designed to be executed via cron (no infinite loops)

- Set up **Husky pre-commit hooks** to enforce:
  - `.env` file is not committed
  - JavaScript files are properly formatted and skips it if no javascript file found
  - Log files are ignored by Git

- Implemented packaging automation:
  - Created `bundle-<timestamp>.zip` containing:
    - `src/`
    - `logs/`
    - `checksums.sha1`
  - Generated SHA1 checksums to verify bundle integrity

- Configured **cron scheduling** to run `healthcheck.sh` every 5 minutes
  - Verified execution via logs
  - Captured cron configuration as proof

### Deliverables

1) `healthcheck.sh`  
2) Husky pre-commit hook screenshots (failed & passed)  
3) `bundle-1770370515.zip`  
4) `checksums.sha1`  
5) Screenshot of scheduled cron job

---

<!-- ~~~~~~~~~~~~~~~~ WEEK 2 ~~~~~~~~~~~~~~~ -->
# Week 2 — Frontend Fundamentals (HTML + CSS + JavaScript)

Week 2 focuses on building strong frontend foundations by understanding semantic HTML, responsive layouts, and JavaScript for DOM manipulation.

---

## Day 1 — HTML5 + Semantic Layout

Day 1 focused on understanding page structure and building a blog layout using **only semantic HTML5**, without CSS or JavaScript.

### Key Learnings

- Used semantic HTML5 elements for proper page structure
- Built layout scaffolding without using `<div>`
- Created forms with basic validation
- Embedded images using `<figure>` and `<img>`
- Applied accessibility basics such as ARIA labels and alt text

### Exercise

Built a **Travel Blog Page** using only semantic HTML, based on the provided Figma reference.

Key features of the blog page:
- Multiple travel blog posts displayed on a single page
- Each blog post structured using `<article>`
- Blog metadata (title, date, author) included
- Images added using `<figure>` and `<figcaption>`
- Navigation using semantic `<nav>`
- Subscription form to receive blog updates

### Deliverables

1) `blog.html`


## Day 2 — CSS Layout Mastery (Flexbox + Grid)

Day 2 focused on building modern, responsive layouts using **Flexbox** and **CSS Grid**, and applying a mobile-first approach to UI development.

### Work Done

- Practiced **CSS selectors and specificity** through selector challenges

- Built layout components using **Flexbox**:
  - Responsive navigation bar
  - Hero section with aligned content

- Implemented a **product grid layout** using **CSS Grid**:
  - 2-column layout on small screens
  - 3-column layout on medium screens
  - 4-column layout on large screens

- Converted a desktop-first layout into a **mobile-first responsive design** using media queries

- Replicated a UI screenshot provided by the mentor using Flexbox

### Deliverables

1) `index.html`  
2) `style.css`  
3) UI comparison screenshots (reference vs implementation)


## Day 3 — JavaScript ES6 + DOM Manipulation

Day 3 focused on using modern JavaScript (ES6) and manipulating the DOM without frameworks.

### Work Done - FAQ Accordion

Built an interactive FAQ accordion using JavaScript.

Features:
- Click to expand/collapse
- Dynamic + / − toggle
- Single active accordion at a time

### Deliverables

1) js-dom-practice/index.html  
2) js-dom-practice/style.css  
3) js-dom-practice/script.js
