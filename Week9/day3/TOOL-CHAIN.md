# TOOL-CHAIN.md — Week 9, Day 3
## Tool-Calling Agents (Code, Files, Database, Search)

---

## Architecture Overview

```
User Query
    ↓
Orchestrator (plan_tasks)          ← reused from Day 2
    ↓
Tool Router (route_task_to_tool)   ← NEW in Day 3
    ├── CodeAgent  → python execution (subprocess)
    ├── DBAgent    → SQLite SQL generation + execution
    └── FileAgent  → CSV/TXT read + LLM analysis
    ↓
Reflection Agent                   ← reused from Day 2
    ↓
Validator Agent                    ← reused from Day 2
    ↓
Final Answer + saved to file
```

---

## Files Added in Day 3

| File | Role |
|------|------|
| `tools/code_executor.py` | LLM writes Python → subprocess executes it |
| `tools/db_agent.py` | LLM writes SQL → SQLite executes it |
| `tools/file_agent.py` | Reads .txt/.csv → LLM analyzes content |
| `main_day3.py` | Day 3 entry point — full tool-chain pipeline |

---

## Tool Agent Details

### CodeAgent (`tools/code_executor.py`)
- **Trigger keywords**: `code`, `python`, `calculate`, `compute`, `script`, `math`
- **Flow**: Task description → LLM writes Python → extract ```python block → subprocess run → capture stdout
- **Safety**: 15-second timeout, temp file execution, cleaned up after run
- **Output**: `{task, code, output}`

### DBAgent (`tools/db_agent.py`)
- **Trigger keywords**: `sql`, `database`, `db`, `query`, `sales data`, `revenue`, `top product`
- **Flow**: Question → LLM writes SQL → extract ```sql block → sqlite3 execute → formatted table
- **Database**: `data/sales.db` (auto-created with 15 sample rows on first run)
- **Schema**: `sales(id, product, category, quantity, revenue, region, sale_date)`
- **Output**: `{question, sql, result}`

### FileAgent (`tools/file_agent.py`)
- **Trigger keywords**: `file`, `csv`, `read`, `analyze`, `insight`, `sales.csv`
- **Flow**: Read file from `data/files/` → pass raw content to LLM → structured analysis
- **Supported formats**: `.txt`, `.csv`
- **Sample data**: `data/files/sales.csv` auto-created on first run
- **Output**: `{filename, content_preview, analysis}`

---

## How to Run Day 3

### Prerequisites
- Free Groq API key from https://console.groq.com (no credit card required)
- `.env` configured with Groq settings (see Environment Variables below)
- Dependencies installed: `pip install -r requirements.txt`

### Run
```bash
python main_day3.py
```

### Sample Queries to Test Each Tool Agent

**FileAgent + CodeAgent path:**
```
Analyze sales.csv and generate the top 5 insights about product performance and revenue
```

**DBAgent path:**
```
Query the sales database to find the top 3 products by total revenue
```

**CodeAgent path:**
```
Write Python code to calculate the compound interest on 10000 at 8% for 5 years
```

**Mixed path (all 3 agents):**
```
Analyze sales.csv file, query the database for top revenue products, and calculate total revenue using Python
```

---

## Tool Routing Logic

The `route_task_to_tool()` function in `main_day3.py` routes each planned subtask by keyword matching on the task description:

```python
if "code" / "python" / "calculate" → CodeAgent
elif "sql" / "database" / "revenue" → DBAgent
elif "file" / "csv" / "analyze"    → FileAgent
else                                → FileAgent (default)
```

---

## Model Used

| Property       | Value                                      |
|----------------|--------------------------------------------|
| Model          | llama-3.3-70b-versatile                    |
| Provider       | Groq (cloud API — free, no credit card)    |
| Endpoint       | https://api.groq.com/openai/v1             |

---

## Environment Variables (`.env`)

```env
OPENAI_API_BASE=https://api.groq.com/openai/v1
OPENAI_API_KEY=your_groq_api_key_here
MODEL_NAME=llama-3.3-70b-versatile
SQLITE_DB_PATH=data/sales.db
FILES_DIR=data/files
```