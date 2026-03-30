# SQL-QA-DOC — Day 4: SQL Question Answering

> **System:** Text → SQL → Answer  
> A pipeline that converts natural language questions into SQL, executes them safely, and returns a summarized answer.

---

## Learning Outcomes

- Convert natural language queries into SQL using an LLM
- Schema-aware reasoning over SQLite/PostgreSQL databases
- SQL query validation and injection-safe execution
- Summarizing raw query results into human-readable answers

---

## Topics Covered

- Schema extraction from live databases
- Prompting patterns for SQL generation
- Query validation (forbidden keyword filtering)
- Error correction and safe execution
- Result summarization using LLM

---

## Project Structure

```
src/
├── pipelines/
│   └── sql_pipeline.py        # Main pipeline orchestrator
├── generator/
│   └── sql_generator.py       # SQL generation + result summarization prompts
├── utils/
│   └── schema_loader.py       # Auto schema extractor from SQLite
└── data/
    └── raw/
        └── sample.db          # SQLite database
```

---

## Pipeline Overview

```
User Question
     │
     ▼
[1] Load Schema          ← schema_loader.py
     │
     ▼
[2] Generate SQL         ← sql_generator.py (LLM prompt)
     │
     ▼
[3] Validate SQL         ← is_safe_sql() in sql_pipeline.py
     │
     ▼
[4] Execute SQL          ← execute_sql() via sqlite3
     │
     ▼
[5] Summarize Result     ← summarize_result() (LLM prompt)
     │
     ▼
  Final Answer
```

---

## Module Reference

### `sql_pipeline.py` — Main Orchestrator

The entry point for the full pipeline. Coordinates all steps end-to-end.

| Function | Description |
|---|---|
| `is_safe_sql(query)` | Blocks dangerous keywords: `DROP`, `DELETE`, `INSERT`, `UPDATE`, `ALTER` |
| `clean_sql(sql)` | Strips markdown code fences (` ```sql ``` `) added by the LLM |
| `execute_sql(query)` | Runs query on SQLite and returns list of row dicts |
| `run_sql_pipeline(question)` | Full pipeline: schema → SQL → validate → execute → summarize |

**Example usage:**
```python
from src.pipelines.sql_pipeline import run_sql_pipeline

result = run_sql_pipeline("Show total sales by artist for 2023.")
print(result["answer"])
```

**Return shape:**
```python
{
    "sql": "SELECT artist, SUM(amount) as total_sales FROM sales WHERE ...",
    "result": [{"artist": "Taylor Swift", "total_sales": 50000}, ...],
    "answer": "In 2023, Taylor Swift led with $50,000 in total sales..."
}
```

---

### `sql_generator.py` — LLM Prompt Layer

Handles two LLM calls: one for SQL generation, one for result summarization.

#### SQL Generation Prompt

```
You are a SQL expert.
Given the database schema: {schema}
Convert the user question into a valid SQLite SQL query.
Rules:
- Only use available tables and columns
- Do NOT hallucinate columns
- Do NOT explain anything
- Return ONLY SQL
```

#### Result Summarization Prompt

```
You are a data analyst.
The SQL query executed was: {sql}
The result of the query is: {result}
Answer the user's question using ONLY this information.
Rules:
- Do NOT say data is missing if query already filters it
- Trust the SQL result
- Be precise and factual
- Use bullet points if helpful
- Always use alias for aggregates (e.g., SUM(amount) as total_sales)
```

| Function | Input | Output |
|---|---|---|
| `generate_sql(question, schema)` | Natural language question + schema string | SQL query string |
| `summarize_result(question, result, sql)` | Question + raw result + SQL | Human-readable answer |

---

### `schema_loader.py` — Auto Schema Extractor

Connects to a SQLite database and extracts table/column metadata automatically.

```python
from src.utils.schema_loader import load_schema

schema = load_schema("src/data/raw/sample.db")
print(schema)
```

**Example output:**
```
Table: sales
  - id (INTEGER)
  - artist (TEXT)
  - amount (REAL)
  - year (INTEGER)

Table: albums
  - id (INTEGER)
  - title (TEXT)
  - artist_id (INTEGER)
```

---

## Security

The pipeline enforces read-only SQL execution by blocking any query that contains the following keywords:

| Keyword | Risk |
|---|---|
| `DROP` | Deletes tables |
| `DELETE` | Removes rows |
| `INSERT` | Adds unauthorized data |
| `UPDATE` | Modifies existing data |
| `ALTER` | Changes schema structure |

If a blocked keyword is detected, the pipeline returns immediately with:
```python
{"error": "Unsafe SQL detected!", "sql": "<generated query>"}
```

---

## Example Run

```
$ python -m src.pipelines.sql_pipeline

Ask SQL question: Show total sales by artist for 2023.

=== SQL PIPELINE ===

Schema:
 Table: sales
  - id (INTEGER)
  - artist (TEXT)
  - amount (REAL)
  - year (INTEGER)

Generated SQL:
 SELECT artist, SUM(amount) AS total_sales
 FROM sales
 WHERE year = 2023
 GROUP BY artist
 ORDER BY total_sales DESC;

Raw Result:
 [{'artist': 'Taylor Swift', 'total_sales': 50000.0}, ...]

=== FINAL ANSWER ===

In 2023, total sales by artist were:
• Taylor Swift — $50,000
• The Weeknd — $38,200
• Drake — $31,500
```

---

## Dependencies

- `sqlite3` — built-in Python SQLite interface
- `re` — regex for SQL cleaning
- `src.generator.llm_client` — underlying LLM call wrapper (`generate_answer`)