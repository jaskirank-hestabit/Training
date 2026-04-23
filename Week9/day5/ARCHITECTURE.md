# NEXUS AI — Architecture

## Overview

NEXUS AI is a fully autonomous multi-agent system built on top of the Week 9 Day 1-4 infrastructure. It orchestrates 9 specialized agents through a structured pipeline to handle complex tasks end-to-end without human intervention.

---

## System Diagram

```
User Query
    │
    ▼
┌─────────────┐
│   PLANNER   │  Decomposes query into 3-5 structured tasks
│   (Step 1)  │  Identifies: code needs, data needs, complexity
└──────┬──────┘
       │  plan dict (JSON)
       ▼
┌─────────────────┐
│  ORCHESTRATOR   │  Builds execution directive
│   (Step 2)      │  Assigns agents, identifies parallelism
└──────┬──────────┘
       │  assignment dict
       ▼
┌──────────────────────────────────────┐
│          PARALLEL WORKERS            │
│                                      │
│  ┌────────────┐  ┌────────────────┐  │
│  │ RESEARCHER │  │    CODER       │  │
│  │ (Step 3)   │  │  (Step 4)      │  │
│  │            │  │                │  │
│  │ FAISS      │  │ ► .py file     │  │
│  │ recall     │  │ ► .md docs     │  │
│  │ (Day 4)    │  │ (Day 3 tools)  │  │
│  └────────────┘  └────────────────┘  │
└──────────────────────┬───────────────┘
                       │ research + code_result
                       ▼
              ┌─────────────────┐
              │    ANALYST      │  Extracts key insights
              │   (Step 5)      │  Findings, risks, opportunities
              └────────┬────────┘
                       │ analysis
                       ▼
              ┌─────────────────┐
              │    CRITIC       │  Self-reflection
              │   (Step 6)      │  Identifies gaps, biases, errors
              └────────┬────────┘
                       │ critique
                       ▼
              ┌─────────────────┐
              │   OPTIMIZER     │  Self-improvement
              │   (Step 7)      │  Addresses all critique points
              └────────┬────────┘
                       │ optimized answer
                       ▼
              ┌─────────────────┐
              │   VALIDATOR     │  Quality gate
              │   (Step 8)      │  PASS → continue
              │                 │  FAIL → re-optimize loop
              └────────┬────────┘
                       │ validated answer
                       ▼
              ┌─────────────────┐
              │   REPORTER      │  Final markdown report
              │   (Step 9)      │  Professional, structured
              └────────┬────────┘
                       │
                       ▼
                 Final Report
                 + Logs
                 + Trace JSON
```

---

## Memory Architecture (Day 4)

All 9 agents share the three-layer memory system:

```
┌──────────────────────────────────────────────────┐
│                  MEMORY SYSTEM                    │
│                                                   │
│  ┌─────────────────┐                             │
│  │  SessionMemory  │  RAM, sliding window (N=20)  │
│  │   (short-term)  │  Clears on process exit      │
│  └─────────────────┘                             │
│                                                   │
│  ┌─────────────────┐                             │
│  │   VectorStore   │  FAISS, disk-persisted       │
│  │    (FAISS)      │  Semantic similarity recall  │
│  │                 │  data/memory/faiss_index.bin  │
│  └─────────────────┘                             │
│                                                   │
│  ┌─────────────────┐                             │
│  │   LongTermDB    │  SQLite, disk-persisted      │
│  │    (SQLite)     │  Episodic + fact storage     │
│  │                 │  data/memory/long_term.db    │
│  └─────────────────┘                             │
└──────────────────────────────────────────────────┘
```

---

## Tool Integration (Day 3)

The Coder agent wraps the Day 3 tool chain:

```
run_coder()
    └── run_code_agent()         (tools/code_executor.py)
            └── execute_python_code()   subprocess sandbox
                    └── saves to data/generated_code/<slug>.py
                    └── saves to data/generated_code/<slug>.md
```

---

## Agent Registry

| Agent | File | Role | Day Origin |
|-------|------|------|-----------|
| Planner | nexus_ai/agents/planner.py | Task decomposition | New (Day 5) |
| Orchestrator | nexus_ai/agents/orchestrator.py | Execution directive | Extends Day 2 |
| Researcher | nexus_ai/agents/researcher.py | Information gathering | Extends Day 1 |
| Coder | nexus_ai/agents/coder.py | Code generation + execution | Wraps Day 3 |
| Analyst | nexus_ai/agents/analyst.py | Insight extraction | New (Day 5) |
| Critic | nexus_ai/agents/critic.py | Self-reflection | New (Day 5) |
| Optimizer | nexus_ai/agents/optimizer.py | Self-improvement | New (Day 5) |
| Validator | nexus_ai/agents/validator.py | Quality gate | Extends Day 2 |
| Reporter | nexus_ai/agents/reporter.py | Final report | New (Day 5) |

---

## Key Design Patterns

- **Planner → Executor → Validator** pattern from Day 2, extended to 9 stages
- **Self-reflection loop**: Critic → Optimizer → Validator (re-run on FAIL)
- **Memory injection**: FAISS recall passed to Researcher to avoid re-research
- **Code persistence**: every generated code artifact saved to disk with explanation
- **Structured logging + tracing** for every step with timestamps

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Agent framework | AutoGen (Microsoft) |
| LLM backend | Grok (llama-3.3-70b-versatile) |
| Vector memory | FAISS (faiss-cpu) |
| Relational memory | SQLite |
| API server | FastAPI (optional, see README) |
| Runtime | Python 3.10+ |