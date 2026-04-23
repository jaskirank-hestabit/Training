"""
nexus_ai/main.py
PROJECT: NEXUS AI — Autonomous Multi-Agent System
Week 9, Day 5 Capstone

Agents: Orchestrator, Planner, Researcher, Coder, Analyst,
        Critic, Optimizer, Validator, Reporter

Uses all Day 1-4 infrastructure:
  - AutoGen agents              (Day 1-2)
  - Tool-calling agents         (Day 3)
  - Memory: STM + FAISS + SQLite (Day 4)

Run:
    python -m nexus_ai.main
    # or from project root:
    python nexus_ai/main.py
"""

import os
import uuid
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nexus_ai.config import NEXUS_CONFIG
from nexus_ai.agents.orchestrator import run_orchestrator
from nexus_ai.agents.planner      import run_planner
from nexus_ai.agents.researcher   import run_researcher
from nexus_ai.agents.coder        import run_coder
from nexus_ai.agents.analyst      import run_analyst
from nexus_ai.agents.critic       import run_critic
from nexus_ai.agents.optimizer    import run_optimizer
from nexus_ai.agents.validator    import run_nexus_validator
from nexus_ai.agents.reporter     import run_reporter
from nexus_ai.utils.logger        import NexusLogger
from nexus_ai.utils.tracer        import NexusTracer

# Memory layer (Day 4)
from memory.long_term      import (
    init_long_term_db,
    save_conversation_turn,
    save_fact,
    count_conversations,
    count_facts,
)
from memory.session_memory import get_session_memory
from memory.vector_store   import get_vector_store


def _persist(stm, vs, session, role, content, agent):
    """Persist a message to all three memory layers (Day 4)."""
    stm.add(role=role, content=content, agent=agent)
    save_conversation_turn(session=session, role=role, agent=agent,
                           content=content[:500])
    vs.add(text=content[:300], mem_type="fact", session=session)


def run_nexus(user_query: str, session: str = None) -> dict:
    """
    Full NEXUS AI 9-step pipeline:
      1. Planner         — structured task decomposition
      2. Orchestrator    — execution directive + role assignment
      3. Researcher      — information gathering (+ FAISS recall)
      4. Coder           — code writing, execution, file save (.py + .md)
      5. Analyst         — data-driven insight extraction
      6. Critic          — self-reflection & gap analysis
      7. Optimizer       — self-improvement based on critique
      8. Validator       — final quality gate (with retry)
      9. Reporter        — polished markdown report
    """
    if session is None:
        session = f"nexus_{uuid.uuid4().hex[:8]}"

    logger = NexusLogger(session)
    tracer = NexusTracer(session)

    logger.log("NEXUS", "BOOT", f"Session {session} | Query: {user_query[:100]}")
    tracer.start("NEXUS_PIPELINE")

    #  Init memory (Day 4) 
    init_long_term_db()
    stm = get_session_memory(session, window_size=20)
    vs  = get_vector_store()

    stm.add(role="user", content=user_query, agent="User")
    save_conversation_turn(session=session, role="user",
                           agent="User", content=user_query)
    vs.add(text=user_query, mem_type="query", session=session)

    # Banner 
    print("\n" + "═" * 70)
    print("  NEXUS AI  —  Autonomous Multi-Agent System")
    print("  Week 9, Day 5 Capstone  |  Built on Days 1-4")
    print("═" * 70)
    print(f"  Session : {session}")
    print(f"  Query   : {user_query}")
    print("═" * 70)

    results = {}

    # 1. PLANNER 
    print("\n  [1/9] PLANNER — Decomposing query into structured plan...")
    tracer.step("PLANNER", "start")
    plan = run_planner(user_query, session=session)
    tracer.step("PLANNER", "done", {"tasks": len(plan.get("tasks", []))})
    logger.log("PLANNER", "PLAN", str(plan)[:200])
    results["plan"] = plan
    task_count = len(plan.get("tasks", []))
    print(f"  ✔ Plan ready — {task_count} tasks | complexity: {plan.get('complexity','?')}")
    _persist(stm, vs, session, "assistant", str(plan), "Planner")

    # 2. ORCHESTRATOR 
    print("\n  [2/9] ORCHESTRATOR — Building execution directive...")
    tracer.step("ORCHESTRATOR", "start")
    assignment = run_orchestrator(user_query, plan, session=session)
    tracer.step("ORCHESTRATOR", "done")
    logger.log("ORCHESTRATOR", "OK", "Directive created")
    results["assignment"] = assignment
    print("  ✔ Orchestration complete")
    _persist(stm, vs, session, "assistant",
             assignment.get("directive", ""), "Orchestrator")

    # 3. RESEARCHER 
    print("\n  [3/9] RESEARCHER — Gathering information (+ FAISS recall)...")
    tracer.step("RESEARCHER", "start")
    research = run_researcher(user_query, plan, session=session)
    tracer.step("RESEARCHER", "done", {"chars": len(research)})
    logger.log("RESEARCHER", "DONE", f"{len(research)} chars")
    results["research"] = research
    print(f"  ✔ Research complete — {len(research):,} chars")
    _persist(stm, vs, session, "assistant", research, "Researcher")

    #  4. CODER 
    print("\n  [4/9] CODER — Writing / executing code if needed...")
    tracer.step("CODER", "start")
    code_result = run_coder(user_query, plan, session=session)
    tracer.step("CODER", "done")
    if code_result.get("skipped"):
        print(f"  ✔ Coder skipped — {code_result.get('reason', '')}")
    else:
        print(f"  ✔ Code written & executed")
        print(f"      .py  → {code_result.get('py_path','')}")
        print(f"      .md  → {code_result.get('md_path','')}")
    logger.log("CODER", "DONE", str(code_result.get("py_path", "skipped")))
    results["code_result"] = code_result
    _persist(stm, vs, session, "assistant", str(code_result), "Coder")

    #  5. ANALYST 
    print("\n  [5/9] ANALYST — Extracting insights...")
    tracer.step("ANALYST", "start")
    analysis = run_analyst(user_query, research, code_result, session=session)
    tracer.step("ANALYST", "done", {"chars": len(analysis)})
    logger.log("ANALYST", "DONE", f"{len(analysis)} chars")
    results["analysis"] = analysis
    print(f"  ✔ Analysis complete — {len(analysis):,} chars")
    _persist(stm, vs, session, "assistant", analysis, "Analyst")

    # 6. CRITIC 
    print("\n  [6/9] CRITIC — Self-reflection & gap analysis...")
    tracer.step("CRITIC", "start")
    critique = run_critic(user_query, analysis, session=session)
    tracer.step("CRITIC", "done")
    logger.log("CRITIC", "DONE", critique[:100])
    results["critique"] = critique
    print("  ✔ Critique complete")
    _persist(stm, vs, session, "assistant", critique, "Critic")

    # 7. OPTIMIZER
    print("\n  [7/9] OPTIMIZER — Self-improvement loop...")
    tracer.step("OPTIMIZER", "start")
    optimized = run_optimizer(user_query, analysis, critique, session=session)
    tracer.step("OPTIMIZER", "done", {"chars": len(optimized)})
    logger.log("OPTIMIZER", "DONE", f"{len(optimized)} chars")
    results["optimized"] = optimized
    print(f"  ✔ Optimization complete — {len(optimized):,} chars")
    _persist(stm, vs, session, "assistant", optimized, "Optimizer")

    # 8. VALIDATOR
    print("\n  [8/9] VALIDATOR — Final quality gate...")
    tracer.step("VALIDATOR", "start")
    validation = run_nexus_validator(user_query, optimized, session=session)
    tracer.step("VALIDATOR", "done", {"verdict": validation["verdict"]})

    if validation["verdict"] == "FAIL":
        print(f"  ✗ FAIL — {validation['reason']} — re-optimizing...")
        feedback_critique = f"Validator feedback: {validation.get('feedback', validation['reason'])}"
        optimized  = run_optimizer(user_query, optimized, feedback_critique, session=session)
        validation = run_nexus_validator(user_query, optimized, session=session)
        results["optimized"] = optimized
        print(f"  ↻ Re-validation: {validation['verdict']}")

    logger.log("VALIDATOR", validation["verdict"], validation["reason"])
    results["validation"] = validation
    print(f"  ✔ Validator: {validation['verdict']} — {validation['reason']}")

    # 9. REPORTER
    print("\n  [9/9] REPORTER — Generating final report...")
    tracer.step("REPORTER", "start")
    final_report = run_reporter(user_query, results, session=session)
    tracer.step("REPORTER", "done")
    logger.log("REPORTER", "DONE", f"{len(final_report)} chars")
    results["final_report"] = final_report
    _persist(stm, vs, session, "assistant", final_report, "Reporter")
    save_fact(session=session,
              fact=final_report[:300].split("\n")[0],
              source="Reporter")

    tracer.end("NEXUS_PIPELINE")

    # Final Output
    print("\n" + "═" * 70)
    print("  NEXUS AI — FINAL REPORT")
    print("═" * 70)
    print(final_report)
    print("\n" + "═" * 70)
    print(f"  Session  : {session}")
    print(f"  Log      : logs/{session}.log")
    print(f"  Trace    : logs/{session}_trace.json")
    print(f"  SQLite   : {count_conversations()} turns | {count_facts()} facts")
    print(f"  FAISS    : {vs.count()} vectors")
    print("═" * 70)

    return {
        "session":      session,
        "query":        user_query,
        "plan":         plan,
        "assignment":   assignment,
        "research":     research,
        "code_result":  code_result,
        "analysis":     analysis,
        "critique":     critique,
        "optimized":    optimized,
        "validation":   validation,
        "final_report": final_report,
    }



DEMO_TASKS = [
    "Plan a startup in AI for healthcare",
    "Generate backend architecture for a scalable app",
    "Analyze CSV & create business strategy",
    "Design a RAG pipeline for 50k documents",
]

if __name__ == "__main__":
    print("\n  NEXUS AI — Autonomous Multi-Agent System")
    print("  Week 9, Day 5 Capstone\n")
    print("  Demo tasks:")
    for i, t in enumerate(DEMO_TASKS, 1):
        print(f"    {i}. {t}")
    print("    5. Enter custom query\n")

    choice = input("  Choose (1-5): ").strip()

    if choice in ("1", "2", "3", "4"):
        query = DEMO_TASKS[int(choice) - 1]
    else:
        query = input("  Enter query: ").strip()
        if not query:
            query = DEMO_TASKS[0]

    run_nexus(query)