import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from orchestrator.planner import plan_tasks
from agents.worker_agent import run_worker_task
from agents.reflection_agent import run_reflection
from agents.validator import run_validation

load_dotenv()

MAX_RETRIES = 2  # max reflection retries on validator FAIL


def run_pipeline(user_query: str):
    print("\n" + "=" * 60)
    print("MULTI-AGENT PIPELINE — DAY 2")
    print("Orchestrator → Workers (parallel) → Reflection → Validator")
    print("=" * 60)
    print(f"USER QUERY: {user_query}\n")

    # STEP 1: Orchestrator plans tasks
    print("─" * 60)
    print("STEP 1 — Orchestrator: Decomposing query into subtasks...")
    tasks = plan_tasks(user_query)

    print("\n[Execution Tree]")
    print(f"  Query: \"{user_query}\"")
    for t in tasks:
        print(f"    ├── {t['id']}: {t['description']}")
    print(f"    ↓")
    print(f"    Reflection → Validator → Final Answer")

    # STEP 2: Parallel Workers 
    print(f"\n{'─' * 60}")
    print(f"STEP 2 — Workers: Running {len(tasks)} tasks in parallel...")

    worker_results = []
    with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
        futures = {executor.submit(run_worker_task, task): task for task in tasks}
        for future in as_completed(futures):
            result = future.result()
            worker_results.append(result)
            print(f"  ✔ {result['task_id']} completed")

    # STEP 3: Reflection
    print(f"\n{'─' * 60}")
    print("STEP 3 — Reflection Agent: Synthesizing worker outputs...")
    improved_answer = run_reflection(user_query, worker_results)

    # STEP 4: Validation loop
    print(f"\n{'─' * 60}")
    print("STEP 4 — Validator: Checking answer quality...")
    final_answer = improved_answer
    validation_result = None

    for attempt in range(1, MAX_RETRIES + 2):  # 1 attempt + up to MAX_RETRIES retries
        validation_result = run_validation(user_query, final_answer)

        if validation_result["verdict"] == "PASS":
            print(f"  Validator PASSED on attempt {attempt}")
            break
        else:
            print(f"  Validator FAILED on attempt {attempt}: {validation_result['reason']}")
            if attempt <= MAX_RETRIES:
                print(f"  Re-running Reflection with validator feedback...")
                # Pass feedback back into reflection
                feedback_task = [{
                    "task_id": "feedback",
                    "description": f"Validator feedback: {validation_result['feedback']}",
                    "result": final_answer
                }]
                final_answer = run_reflection(
                    user_query,
                    worker_results + feedback_task
                )
            else:
                print(f"  Max retries reached. Using last answer.")

    # RESULTS
    print("\n" + "=" * 60)
    print("PIPELINE RESULTS — DAY 2")
    print("=" * 60)

    print("\n TASK BREAKDOWN (Execution Tree):")
    for t in tasks:
        print(f"  [{t['id']}] {t['description']}")

    print("\n WORKER OUTPUTS:")
    for r in worker_results:
        print(f"\n  [{r['task_id']}] {r['description']}")
        print(f"  {r['result'][:300]}{'...' if len(r['result']) > 300 else ''}")

    print(f"\n REFLECTION OUTPUT (first 400 chars):")
    print(f"  {improved_answer[:400]}{'...' if len(improved_answer) > 400 else ''}")

    print(f"\n VALIDATION:")
    print(f"  Verdict : {validation_result['verdict']}")
    print(f"  Reason  : {validation_result['reason']}")

    print(f"\n FINAL ANSWER:\n{final_answer}")
    print("=" * 60)

    return {
        "query": user_query,
        "tasks": tasks,
        "worker_results": worker_results,
        "reflection": improved_answer,
        "validation": validation_result,
        "final_answer": final_answer,
    }


if __name__ == "__main__":
    print("\n MULTI-AGENT SYSTEM — DAY 2")
    print("=" * 60)
    user_input = input("Enter your query: ").strip()
    if not user_input:
        print("No query entered. Using default.")
        user_input = "Explain the Planner-Executor pattern in multi-agent AI systems and how it differs from single-agent systems."
    run_pipeline(user_input)