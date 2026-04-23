import os
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

from orchestrator.planner    import plan_tasks
from agents.worker_agent     import run_worker_task
from agents.reflection_agent import run_reflection
from agents.validator        import run_validation

from memory.session_memory import get_session_memory
from memory.vector_store   import get_vector_store
from memory.long_term      import (
    init_long_term_db,
    save_conversation_turn,
    save_fact,
    get_conversation_history,
    get_facts,
    count_conversations,
    count_facts,
)
from memory.memory_agent import run_memory_agent

load_dotenv()

MAX_RETRIES = 1


#  HELPER — print memory state

def _print_memory_state(session: str):
    stm = get_session_memory(session)
    vs  = get_vector_store()
    print(f"\n MEMORY STATE (session: {session})")
    print(f"  Short-Term (RAM window) : {len(stm)} messages")
    print(f"  Vector Store (FAISS)    : {vs.count()} entries")
    print(f"  Long-Term DB (SQLite)   : {count_conversations()} conversation turns, "
          f"{count_facts()} facts")

    history = get_conversation_history(session, limit=3)
    if history:
        print(f"\n  Recent SQLite turns (last {len(history)}):")
        for h in history:
            print(f"    [{h['ts'][:19]}] {h['agent']}: {h['content'][:80]}...")

    facts = get_facts(session=session, limit=3)
    if facts:
        print(f"\n  Stored facts (last {len(facts)}):")
        for f in facts:
            print(f"    • {f['fact'][:100]}...")


#  MODE 1 — FULL PIPELINE WITH MEMORY

def run_day4_pipeline(user_query: str, session: str = None):
    if session is None:
        session = f"day4_{uuid.uuid4().hex[:8]}"

    print("\n" + "=" * 60)
    print("MULTI-AGENT PIPELINE — DAY 4 (MEMORY SYSTEM)")
    print("SessionMemory + VectorStore (FAISS) + LongTermDB (SQLite)")
    print("=" * 60)
    print(f"USER QUERY : {user_query}")
    print(f"SESSION ID : {session}\n")

    # Initialise all memory systems
    init_long_term_db()
    stm = get_session_memory(session, window_size=10)
    vs  = get_vector_store()

    # STEP 0: Recall from memory
    print("─" * 60)
    print("STEP 0 — Memory Recall: Searching all memory layers...")

    # Vector store: semantic recall
    similar_vectors = vs.search(user_query, top_k=3, session=session)
    if similar_vectors:
        print(f"  VectorStore: {len(similar_vectors)} similar past entries found")
        for m in similar_vectors:
            print(f"    [{m['type']}] {m['text'][:70]}...")
    else:
        print("  VectorStore: No similar past entries (first run or new session)")

    # SQLite: recent conversation turns
    prior_turns = get_conversation_history(session, limit=5)
    prior_facts = get_facts(session=session, limit=5)
    if prior_turns:
        print(f"  LongTermDB : {len(prior_turns)} prior turns found")
    else:
        print("  LongTermDB : No prior turns (fresh session)")

    # Persist incoming query to all layers
    stm.add(role="user", content=user_query, agent="User")
    save_conversation_turn(session=session, role="user",
                           agent="User", content=user_query)
    vs.add(text=user_query, mem_type="query", session=session)

    # STEP 1: Orchestrator
    print("─" * 60)
    print("STEP 1 — Orchestrator: Decomposing query into subtasks...")
    tasks = plan_tasks(user_query)

    print("\n[Execution Tree]")
    print(f"  Query: \"{user_query}\"")
    for t in tasks:
        print(f"    ├── {t['id']}: {t['description']}")
    print("    ↓")
    print("    Workers (parallel) → Reflection → Validator → Final Answer")

    # STEP 2: Parallel Workers
    print(f"\n{'─' * 60}")
    print(f"STEP 2 — Workers: Running {len(tasks)} tasks in parallel...")

    worker_results = []
    with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
        futures = {executor.submit(run_worker_task, task): task for task in tasks}
        for future in as_completed(futures):
            result = future.result()
            worker_results.append(result)

            # Persist worker output to all memory layers
            stm.add(role="assistant", content=result["result"],
                    agent=result["task_id"])
            save_conversation_turn(session=session, role="assistant",
                                   agent=result["task_id"],
                                   content=result["result"][:500])
            vs.add(text=f"[{result['task_id']}] {result['result'][:200]}",
                   mem_type="fact", session=session)
            # Save first sentence as a distilled fact to SQLite
            fact = result["result"][:200].split("\n")[0]
            save_fact(session=session, fact=fact,
                      source=result["task_id"])

            print(f"  ✔ {result['task_id']} completed → stored in all memory layers")

    # STEP 3: Memory-aware Reflection
    print(f"\n{'─' * 60}")
    print("STEP 3 — Reflection Agent: Synthesising with memory context...")

    # Build memory context block to inject
    memory_context_parts = []
    if similar_vectors:
        memory_context_parts.append(
            "\n".join(f"[vector:{m['type']}] {m['text']}"
                      for m in similar_vectors)
        )
    if prior_facts:
        memory_context_parts.append(
            "\n".join(f"[fact] {f['fact']}" for f in prior_facts)
        )

    reflection_input = worker_results
    if memory_context_parts:
        reflection_input = [{
            "task_id":     "memory_context",
            "description": "Prior memory context injected from all memory layers",
            "result":      "\n".join(memory_context_parts),
        }] + worker_results

    improved_answer = run_reflection(user_query, reflection_input)
    stm.add(role="assistant", content=improved_answer, agent="ReflectionAgent")
    save_conversation_turn(session=session, role="assistant",
                           agent="ReflectionAgent", content=improved_answer[:500])

    # STEP 4: Validation loop
    print(f"\n{'─' * 60}")
    print("STEP 4 — Validator: Checking answer quality...")
    final_answer      = improved_answer
    validation_result = None

    for attempt in range(1, MAX_RETRIES + 2):
        validation_result = run_validation(user_query, final_answer)

        if validation_result["verdict"] == "PASS":
            print(f"  ✔ Validator PASSED on attempt {attempt}")
            break
        else:
            print(f"  ✗ Validator FAILED (attempt {attempt}): "
                  f"{validation_result['reason']}")
            if attempt <= MAX_RETRIES:
                print("  ↻ Re-running Reflection with validator feedback...")
                feedback_task = [{
                    "task_id":     "feedback",
                    "description": f"Validator feedback: {validation_result['feedback']}",
                    "result":      final_answer,
                }]
                final_answer = run_reflection(
                    user_query, reflection_input + feedback_task
                )
            else:
                print("  ⚠ Max retries reached. Using last answer.")

    # STEP 5: Persist final answer to all memory layers
    stm.add(role="assistant", content=final_answer, agent="FinalAnswer")
    save_conversation_turn(session=session, role="assistant",
                           agent="FinalAnswer", content=final_answer[:500])
    vs.add(text=final_answer, mem_type="summary", session=session)
    save_fact(session=session,
              fact=final_answer[:300].split("\n")[0],
              source="FinalAnswer")

    # RESULTS
    print("\n" + "=" * 60)
    print("PIPELINE RESULTS — DAY 4")
    print("=" * 60)

    print("\n TASK BREAKDOWN:")
    for t in tasks:
        print(f"  [{t['id']}] {t['description']}")

    _print_memory_state(session)

    print(f"\n VALIDATION:")
    print(f"  Verdict : {validation_result['verdict']}")
    print(f"  Reason  : {validation_result['reason']}")

    print(f"\n FINAL ANSWER:\n{final_answer}")
    print("=" * 60)
    print(f"\n[Memory persisted → data/memory/ | Session: {session}]")
    print(f"  • data/memory/faiss_index.bin  (VectorStore)")
    print(f"  • data/memory/long_term.db     (LongTermDB)")

    return {
        "query":          user_query,
        "session":        session,
        "tasks":          tasks,
        "worker_results": worker_results,
        "reflection":     improved_answer,
        "validation":     validation_result,
        "final_answer":   final_answer,
        "stm_snapshot":   stm.get_window(),
        "ltm_turns":      count_conversations(),
        "ltm_facts":      count_facts(),
        "vector_count":   vs.count(),
    }


#  MODE 2 — INTERACTIVE MEMORY-ONLY DEMO

def run_memory_only_mode(session: str = "interactive_demo"):
    """
    Interactive loop that purely demonstrates the three-layer memory system
    without running the full orchestration pipeline.

    Commands:
      stats   — show memory counts across all three layers
      history — show last 5 SQLite conversation turns
      facts   — show stored facts from SQLite
      quit    — exit
    """
    init_long_term_db()
    stm = get_session_memory(session)
    vs  = get_vector_store()

    print("\n" + "=" * 60)
    print("MEMORY-ONLY MODE — DAY 4")
    print("Three-layer memory: SessionMemory + VectorStore + LongTermDB")
    print("Commands: stats | history | facts | quit")
    print("=" * 60)
    print(f"Session: {session}")
    print(f"LongTermDB loaded: {count_conversations()} turns, {count_facts()} facts")

    while True:
        try:
            query = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not query:
            continue

        if query.lower() == "quit":
            break

        if query.lower() == "stats":
            _print_memory_state(session)
            continue

        if query.lower() == "history":
            turns = get_conversation_history(session, limit=5)
            print(f"\n  Last {len(turns)} conversation turns (SQLite):")
            for h in turns:
                print(f"    [{h['ts'][:19]}] {h['agent']}: {h['content'][:100]}...")
            continue

        if query.lower() == "facts":
            facts = get_facts(session=session, limit=10)
            print(f"\n  Stored facts (SQLite) — {len(facts)} found:")
            for f in facts:
                print(f"    [{f['ts'][:10]}] {f['fact'][:120]}")
            continue

        result = run_memory_agent(user_query=query, session=session)
        print(f"\nAgent: {result['answer']}")
        print(
            f"  [STM: {len(stm)} | "
            f"FAISS: {vs.count()} | "
            f"SQLite: {count_conversations()} turns, {count_facts()} facts]"
        )


#  ENTRY POINT

if __name__ == "__main__":
    print("\n MULTI-AGENT SYSTEM — DAY 4 (MEMORY SYSTEMS)")
    print("=" * 60)
    print("Choose mode:")
    print("  1 — Full pipeline with memory (Orchestrator → Workers → Reflection → Validator)")
    print("  2 — Interactive memory-only agent (demonstrates all 3 memory layers)")

    choice = input("\nEnter 1 or 2: ").strip()

    if choice == "2":
        run_memory_only_mode(session="interactive_demo")
    else:
        user_input = input("\nEnter your query: ").strip()
        if not user_input:
            print("No query entered. Using default.")
            user_input = (
                "Explain short-term vs long-term memory in AI agents "
                "and why both are needed."
            )
        run_day4_pipeline(user_input)