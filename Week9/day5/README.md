# NEXUS AI — Autonomous Multi-Agent System
> Week 9, Day 5 Capstone — Built on Days 1-4

## What is NEXUS AI?

NEXUS AI is a fully autonomous 9-agent pipeline that can:
- Plan and decompose any complex query
- Research, code, analyse, self-critique, self-improve, validate, and report
- Persist memory across sessions (FAISS + SQLite)
- Save generated code to `.py` + `.md` files automatically
- Log every step with timestamps and execution traces

---

## Prerequisites

Make sure you have completed Days 1-4 and have:
- A free **Groq API key** (no credit card required — see below)
- `requirements.txt` dependencies installed
- `.env` configured

> **No Ollama or local model needed.** NEXUS AI now runs on Groq's cloud API,
> which is free and significantly faster than local models.

---

## Getting Your Free Groq API Key

1. Go to **https://console.groq.com**
2. Sign up / log in (Google login works)
3. Click **API Keys** in the left sidebar
4. Click **Create API Key**
5. Copy the key and paste it into your `.env` file

---

## Installation

```bash
# 1. Install dependencies (if not already done from Day 1-4)
pip install pyautogen==0.2.35 openai python-dotenv faiss-cpu numpy

# 2. Configure your .env (see Environment Variables section below)
nano .env   # or open in VS Code

# 3. Verify the connection
python -c "
import openai, os
from dotenv import load_dotenv
load_dotenv()
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'), base_url=os.getenv('OPENAI_API_BASE'))
resp = client.chat.completions.create(model=os.getenv('MODEL_NAME'), messages=[{'role':'user','content':'Say GROQ CONNECTED'}], max_tokens=10)
print(resp.choices[0].message.content)
"
```

If it prints `GROQ CONNECTED` (or similar), you're ready to run NEXUS AI.

---

## Running NEXUS AI

### Interactive Mode (recommended)
```bash
python -m nexus_ai.main
```
You will see a menu:
```
  Demo tasks:
    1. Plan a startup in AI for healthcare
    2. Generate backend architecture for a scalable app
    3. Analyze CSV & create business strategy
    4. Design a RAG pipeline for 50k documents
    5. Enter custom query
```

### Direct Python import
```python
from nexus_ai.main import run_nexus

result = run_nexus("Plan a startup in AI for healthcare")
print(result["final_report"])
```

### Custom query example
```bash
python -m nexus_ai.main
```

---

## Code Generation Feature

When your query involves code (e.g. "write binary search", "implement fibonacci"), NEXUS AI will:

1. Write Python code using the Day 3 CodeAgent
2. Execute it in a sandboxed subprocess
3. Save the code to `data/generated_code/<task_name>.py`
4. Save an explanation to `data/generated_code/<task_name>.md`
5. Print both paths to the terminal

Example output:
```
  [Coder] ✔ Code saved  → /your/project/data/generated_code/binary_search.py
  [Coder] ✔ Docs saved  → /your/project/data/generated_code/binary_search.md
```

---

## Output Files

After each run:

| File | Description |
|------|-------------|
| `logs/<session>.log` | Structured log of all agent steps |
| `logs/<session>_trace.json` | Execution trace with timings |
| `data/generated_code/*.py` | Generated Python code |
| `data/generated_code/*.md` | Code explanation in markdown |
| `data/memory/faiss_index.bin` | FAISS vector store (Day 4) |
| `data/memory/long_term.db` | SQLite episodic memory (Day 4) |

---

## Testing Each Demo Task

### Task 1 — AI Healthcare Startup
```bash
python -m nexus_ai.main
# Choose: 1
```
Expected: Strategic plan covering market, technology, regulations, go-to-market.

### Task 2 — Backend Architecture
```bash
python -m nexus_ai.main
# Choose: 2
```
Expected: Architecture covering microservices/monolith decision, DB choice, caching, scaling.

### Task 3 — CSV Analysis + Business Strategy
```bash
python -m nexus_ai.main
# Choose: 3
```
Expected: Analyst pulls insights from research, strategic recommendations.

### Task 4 — RAG Pipeline Design
```bash
python -m nexus_ai.main
# Choose: 4
```
Expected: Step-by-step RAG architecture, chunking strategy, vector DB choice, retrieval design.

### Custom — Code Generation
```bash
python -m nexus_ai.main
# Choose: 5
# Type: write a binary search algorithm in Python
```
Expected: Code saved to `data/generated_code/`, paths printed to terminal.

---

## Viewing Logs

```bash
# View session log
cat logs/<session_id>.log

# View trace
cat logs/<session_id>_trace.json

# List all sessions
ls logs/
```

---

## Project Structure

```
nexus_ai/
├── main.py             ← Entry point (run this)
├── config.py           ← All config in one place
├── agents/
│   ├── planner.py      ← Step 1: task decomposition
│   ├── orchestrator.py ← Step 2: execution directive
│   ├── researcher.py   ← Step 3: information gathering
│   ├── coder.py        ← Step 4: code generation + file save
│   ├── analyst.py      ← Step 5: insight extraction
│   ├── critic.py       ← Step 6: self-reflection
│   ├── optimizer.py    ← Step 7: self-improvement
│   ├── validator.py    ← Step 8: quality gate
│   └── reporter.py     ← Step 9: final report
└── utils/
    ├── logger.py       ← Structured logging
    └── tracer.py       ← Execution tracing
```

---

## Environment Variables (.env)

```env
# ── LLM Backend ───
OPENAI_API_BASE=https://api.groq.com/openai/v1
OPENAI_API_KEY=your_groq_api_key_here
MODEL_NAME=llama-3.3-70b-versatile

# ── Paths ─────────────────────────────────────────────────
SQLITE_DB_PATH=data/sales.db
FILES_DIR=data/files
MEMORY_DIR=data/memory
LOGS_DIR=logs
CODE_OUTPUT_DIR=data/generated_code

# ── Pipeline tuning ───────────────────────────────────────
MAX_TOKENS=1024
TEMPERATURE=0.4
MAX_RETRIES=1
```

### Why these values?

| Variable | Value | Reason |
|----------|-------|--------|
| `OPENAI_API_BASE` | `https://api.groq.com/openai/v1` | Groq's OpenAI-compatible endpoint |
| `MODEL_NAME` | `llama-3.3-70b-versatile` | Best free Groq model for multi-agent tasks |
| `MAX_TOKENS` | `1024` | Increased from 768 — cloud API has no RAM limit |

---

## Switching LLM Backends

NEXUS AI is backend-agnostic — only `.env` needs to change. No code changes required.

| Backend | `OPENAI_API_BASE` | `MODEL_NAME` |
|---------|-------------------|--------------|
| **Groq** | `https://api.groq.com/openai/v1` | `llama-3.3-70b-versatile` |
| Google Gemini | `https://generativelanguage.googleapis.com/v1beta/openai/` | `gemini-2.0-flash` |
| Ollama (local) | `http://localhost:11434/v1` | `phi3` / `mistral` |

---

## How Day 1-4 Code is Reused

| Day | Component | Used by NEXUS |
|-----|-----------|--------------|
| Day 1 | `agents/research_agent.py` | Pattern basis for Researcher |
| Day 2 | `orchestrator/planner.py` | Orchestrator agent pattern |
| Day 2 | `agents/worker_agent.py` | Worker pattern used in pipeline |
| Day 2 | `agents/reflection_agent.py` | Critic + Optimizer pattern |
| Day 2 | `agents/validator.py` | Validator wraps Day 2 logic |
| Day 3 | `tools/code_executor.py` | Coder calls `run_code_agent()` directly |
| Day 3 | `tools/db_agent.py` | Available for Analyst data queries |
| Day 3 | `tools/file_agent.py` | Available for file-based tasks |
| Day 4 | `memory/session_memory.py` | All agents share STM |
| Day 4 | `memory/vector_store.py` | Researcher uses FAISS recall |
| Day 4 | `memory/long_term.py` | Every step persisted to SQLite |