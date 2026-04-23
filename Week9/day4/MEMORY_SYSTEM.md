# MEMORY-SYSTEM.md — Week 9, Day 4

## What Day 4 Builds

A three-layer memory architecture added to the existing multi-agent pipeline.

---

## Three Memory Layers

| Layer | File | Storage | Scope | Spec Term |
|-------|------|---------|-------|-----------|
| Short-term | `memory/session_memory.py` | RAM (deque) | Current session only | Session memory |
| Vector | `memory/vector_store.py` | FAISS on disk | Cross-session semantic recall | Vector memory |
| Long-term | `memory/long_term.py` | SQLite (`long_term.db`) | Permanent, all sessions | Long-term memory |

---

## Architecture

```
New User Query
      │
      ▼
┌─────────────────────────────────────────┐
│  STEP 0 — Memory Recall                 │
│  VectorStore.search(query)   → similar  │
│  LongTermDB.get_history()    → episodic │
│  Both injected into agent prompt        │
└──────────────────┬──────────────────────┘
                   │
                   ▼
        Orchestrator → 2-3 Worker Agents (parallel)
                   │
           Each worker output →  SessionMemory.add()
                             →  LongTermDB.save_turn()
                             →  LongTermDB.save_fact()
                             →  VectorStore.add()
                   │
                   ▼
        Reflection Agent (context-aware)
                   │
                   ▼
        Validator → Final Answer
                   │
                   ▼
        Final Answer → all 3 memory layers saved
```

---

## Layer 1 — Session Memory (`session_memory.py`)

Short-term, RAM-only sliding window.

```python
from memory.session_memory import get_session_memory

stm = get_session_memory("my_session", window_size=10)
stm.add(role="user", content="What is FAISS?", agent="User")
stm.add(role="assistant", content="FAISS is ...", agent="MemoryAgent")

print(stm.get_context_string())  # formatted block for prompt injection
print(len(stm))                   # 2
stm.clear()                       # wipe session
```

- Implemented as `collections.deque(maxlen=10)`
- One instance per session via `get_session_memory(session_id)`
- Lost when process exits — pure working memory

---

## Layer 2 — Vector Store (`vector_store.py`)

FAISS-backed semantic similarity search. Persists to disk.

```python
from memory.vector_store import get_vector_store

vs = get_vector_store()
vs.add("FAISS is a Facebook AI similarity search library",
       mem_type="fact", session="s1")

results = vs.search("similarity search", top_k=3)
for r in results:
    print(r["text"], r["score"])   # score = L2 distance (lower = more similar)
```

- Uses `faiss.IndexFlatL2` (exact nearest neighbour, no approximation)
- Embedding: character-bigram hash (128-dim, deterministic, no API needed)
- Persists to `data/memory/faiss_index.bin` + `data/memory/vector_meta.json`

### Memory types stored

| type | When |
|------|------|
| `query` | User's input |
| `answer` | Agent's response |
| `fact` | Worker output snippets |
| `summary` | Final validated answers |

---

## Layer 3 — Long-Term DB (`long_term.py`)

SQLite database. Two tables: conversations (episodic) and facts (semantic).

```python
from memory.long_term import (
    init_long_term_db,
    save_conversation_turn,
    save_fact,
    get_conversation_history,
    get_facts,
)

init_long_term_db()   # creates data/memory/long_term.db

# Save a conversation turn (episodic memory)
save_conversation_turn(session="s1", role="user",
                       agent="User", content="What is FAISS?")

# Save a distilled fact (semantic memory)
save_fact(session="s1",
          fact="FAISS is a vector similarity search library by Facebook",
          source="MemoryAgent")

# Retrieve
history = get_conversation_history("s1", limit=10)
facts   = get_facts(session="s1", limit=5)
```

### Tables

**conversations** — episodic memory
```sql
id | session | role | agent | content | ts
```

**facts** — semantic memory (distilled knowledge)
```sql
id | session | fact | source | ts
```

---

## Memory-Aware Agent (`memory_agent.py`)

Wraps an AutoGen AssistantAgent. Its system prompt is dynamically built from all three layers before every call.

```
=== SHORT-TERM MEMORY (current session window) ===
[timestamp] User (user): What is FAISS?
[timestamp] MemoryAgent (assistant): FAISS is ...

=== EPISODIC MEMORY (recent SQLite turns) ===
[timestamp] User: What did we discuss?

=== SEMANTIC MEMORY (stored facts) ===
• FAISS is a Facebook AI similarity search library

=== VECTOR RECALL (similar past context via FAISS) ===
• [answer @ 2026-04-17] FAISS stands for ...
```

---

## Model Used

| Property       | Value                                      |
|----------------|--------------------------------------------|
| Model          | llama-3.3-70b-versatile                    |
| Provider       | Groq (cloud API — free, no credit card)    |
| Endpoint       | https://api.groq.com/openai/v1             |

---

## Query Flow (per the spec)

```
New Query
  → Search VectorStore for similar past context   (similarity-based recall)
  → Fetch recent turns from LongTermDB            (episodic recall)
  → Inject both into agent system prompt          (context injection)
  → Generate answer with full context             (generate with context)
  → Save query + answer to all 3 layers           (conversation stored)
  → Save distilled fact to SQLite facts table     (important facts summarized)
  → Add answer embedding to FAISS                 (stored in FAISS)
```

This directly maps to the spec's stated flow:
> New Query → Search memory → Fetch similar context → Inject in prompt → Generate with context

---

## Does Day 4 Require Days 1–3?

Yes. `main_day4.py` imports:

| Import | From |
|--------|------|
| `orchestrator.planner.plan_tasks` | Day 2 |
| `agents.worker_agent.run_worker_task` | Day 2 |
| `agents.reflection_agent.run_reflection` | Day 2 |
| `agents.validator.run_validation` | Day 2 |

The `memory/` package is self-contained and adds no changes to Day 1/2/3 files.

---

## Run

```bash
# Run Day 4
python main_day4.py
```

---

## How to Test

**Test 1 — Full pipeline, first run (no prior memories):**
```bash
python main_day4.py   # choose 1
# Query: "Explain short-term vs long-term memory in AI agents"
# Step 0 should say: "No similar past entries"
# End: check data/memory/long_term.db exists
```

**Test 2 — Interactive mode, demonstrate recall:**
```bash
python main_day4.py   # choose 2
# Type: "What is FAISS?"
# Type: "What did we just discuss?"    ← should recall FAISS
# Type: facts                           ← see SQLite facts table
# Type: history                         ← see SQLite conversation turns
# Type: stats                           ← see all 3 memory layer counts
```

**Test 3 — Verify disk persistence:**
```bash
ls data/memory/
# faiss_index.bin   vector_meta.json   long_term.db

# Inspect SQLite directly
sqlite3 data/memory/long_term.db "SELECT * FROM conversations;"
sqlite3 data/memory/long_term.db "SELECT * FROM facts;"
```

**Test 4 — Cross-session memory (LTM persists across runs):**
```bash
# Run once, ask something
python main_day4.py   # mode 2, ask "What is a vector database?"

# Exit (Ctrl+C), run again with same session name
python main_day4.py   # mode 2, ask "What did we discuss earlier?"
# VectorStore and SQLite will surface the prior answer
```

---

## Episodic vs Semantic Memory (as per spec)

| Concept | Implementation |
|---------|---------------|
| **Episodic memory** | `conversations` table in `long_term.db` — every turn with timestamp and agent name |
| **Semantic memory** | `facts` table in `long_term.db` — distilled, agent-summarised knowledge |
| **Working memory** | `session_memory.py` — in-RAM sliding window for current session |
| **Associative recall** | `vector_store.py` — FAISS similarity search across all stored text |

---

## Environment Config (`.env`)

```env
OPENAI_API_BASE=https://api.groq.com/openai/v1
OPENAI_API_KEY=your_groq_api_key_here
MODEL_NAME=llama-3.3-70b-versatile
SQLITE_DB_PATH=data/sales.db
FILES_DIR=data/files
MEMORY_DIR=data/memory
```