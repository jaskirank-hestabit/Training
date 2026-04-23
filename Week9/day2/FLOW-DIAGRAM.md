# FLOW-DIAGRAM.md — Day 2: Multi-Agent Orchestration

## Architecture Overview

```
USER QUERY
    │
    ▼
┌─────────────────────────────────────────────────────┐
│              ORCHESTRATOR / PLANNER                 │
│  - Receives user query                              │
│  - Breaks into subtasks (DAG)                       │
│  - Assigns tasks to worker agents                   │
│  - Tracks execution state                           │
└────────────┬────────────────────────────────────────┘
             │ creates task graph (steps list)
             ▼
┌─────────────────────────────────────────────────────┐
│           PARALLEL WORKER AGENTS                    │
│                                                     │
│   ┌──────────────┐     ┌──────────────┐             │
│   │  Worker-1    │     │  Worker-2    │  ...        │
│   │ (subtask-1)  │     │ (subtask-2)  │             │
│   └──────┬───────┘     └──────┬───────┘             │
│          │                   │                      │
└──────────┼───────────────────┼──────────────────────┘
           │  partial results  │
           ▼                   ▼
┌─────────────────────────────────────────────────────┐
│             REFLECTION AGENT                        │
│  - Receives all worker outputs                      │
│  - Identifies gaps, contradictions                  │
│  - Improves and synthesizes the combined answer     │
└────────────────────────┬────────────────────────────┘
                         │ improved answer
                         ▼
┌─────────────────────────────────────────────────────┐
│               VALIDATOR AGENT                       │
│  - Checks logic, accuracy, completeness             │
│  - Returns PASS or FAIL with feedback               │
│  - On FAIL → loops back to Reflection Agent         │
└────────────────────────┬────────────────────────────┘
                         │ validated answer
                         ▼
                    FINAL ANSWER
```

---

## Execution Tree (Detailed)

```
Step 0: User submits query
    └── Orchestrator.plan(query)
            ├── Returns: List[Task]  e.g. [task_1, task_2, task_3]
            └── Each task has: id, description, assigned_worker

Step 1: Worker Agents run in parallel (ThreadPoolExecutor)
    ├── Worker(task_1) → result_1
    ├── Worker(task_2) → result_2
    └── Worker(task_n) → result_n

Step 2: Reflection Agent
    └── Input: {query, tasks, worker_results}
        Output: improved_answer (synthesized)

Step 3: Validator Agent
    └── Input: {query, improved_answer}
        ├── PASS → return final_answer
        └── FAIL → feedback → retry Reflection (max 2 retries)

Step 4: Output final validated answer
```

---

## Agent Registry

| Agent             | Role                              | File                         |
|-------------------|-----------------------------------|------------------------------|
| Orchestrator      | Planner, task decomposer          | orchestrator/planner.py      |
| WorkerAgent       | Executes a single assigned task   | agents/worker_agent.py       |
| ReflectionAgent   | Synthesizes and improves outputs  | agents/reflection_agent.py   |
| ValidatorAgent    | Validates final answer            | agents/validator.py          |

---

## DAG Concept

The Orchestrator generates a **Directed Acyclic Graph (DAG)** of tasks:

```
         [query]
        /   |   \
   [T1]  [T2]  [T3]     ← parallel worker tasks (no dependencies)
        \   |   /
       [Reflection]
            |
        [Validator]
            |
       [Final Answer]
```

All Worker tasks are independent (no inter-task dependencies in this design), so they execute fully in parallel before the Reflection and Validator stages.

---

## Message Protocol

Each message passed between agents follows this structure:

```python
{
  "from": "AgentName",
  "to": "AgentName",
  "task_id": "task_1",          # optional
  "content": "...",
  "status": "in_progress" | "complete" | "failed"
}
```

---

## Model Used

| Property       | Value                                      |
|----------------|--------------------------------------------|
| Model          | llama-3.3-70b-versatile                    |
| Provider       | Groq (cloud API — free, no credit card)    |
| Endpoint       | https://api.groq.com/openai/v1             |

---

## Files Produced (Day 2)

```
orchestrator/
    planner.py              ← Orchestrator + task decomposition logic
agents/
    worker_agent.py         ← Generic worker that executes any task
    reflection_agent.py     ← Synthesizes and improves worker outputs
    validator.py            ← Validates the final answer
main_day2.py                ← Entry point, wires up the full pipeline
FLOW-DIAGRAM.md             ← This file
```