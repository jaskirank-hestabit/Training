import os
from dotenv import load_dotenv
from tools.code_executor import run_code_agent
from tools.db_agent import run_db_agent, init_sample_db
from tools.file_agent import run_file_agent, create_sample_csv, write_file
from orchestrator.planner import plan_tasks
from agents.reflection_agent import run_reflection
from agents.validator import run_validation

load_dotenv()

MAX_RETRIES = 1
FILES_DIR = os.getenv("FILES_DIR", "data/files")


# Helpers

def detect_pipeline_type(user_query: str) -> str:
    q = user_query.lower()
    if any(k in q for k in ["sql", "database", "db", "query", "top product", "sales data"]):
        return "db"
    if any(k in q for k in ["sales.csv", "analyze file", "read file", "csv file", "file analysis"]):
        return "file"
    return "code"


def route_task_to_tool(task: dict, pipeline_type: str) -> dict:
    desc = task["description"].lower()
    task_id = task["id"]

    # Explicit DB keywords always win
    if any(k in desc for k in ["sql", "database", "db", "query", "revenue", "top product", "sales data"]):
        print(f"  → [DBAgent] handling {task_id}")
        result = run_db_agent(task["description"])
        return {
            "task_id": task_id,
            "description": task["description"],
            "tool": "DBAgent",
            "result": f"SQL:\n{result['sql']}\n\nResult:\n{result['result']}",
            "code_file": None,
        }

    # Explicit file keywords always win
    if any(k in desc for k in ["sales.csv", "read file", "csv file", "file content"]):
        print(f"  → [FileAgent] handling {task_id}")
        result = run_file_agent("sales.csv", task["description"])
        return {
            "task_id": task_id,
            "description": task["description"],
            "tool": "FileAgent",
            "result": result["analysis"],
            "code_file": None,
        }

    # Code keywords
    if any(k in desc for k in ["code", "python", "script", "compute", "calculate", "formula",
                                "write", "implement", "function", "modify", "program", "interest",
                                "algorithm", "math", "number", "value", "test case"]):
        print(f"  → [CodeAgent] handling {task_id}")
        result = run_code_agent(task["description"], task_id=task_id)
        return {
            "task_id": task_id,
            "description": task["description"],
            "tool": "CodeAgent",
            "result": f"Code:\n{result['code']}\n\nOutput:\n{result['output']}",
            "code_file": result.get("code_file"),
        }

    # Fallback: use pipeline_type detected from the ORIGINAL query
    print(f"  → [{pipeline_type.upper()}Agent-default] handling {task_id}")
    if pipeline_type == "db":
        result = run_db_agent(task["description"])
        return {
            "task_id": task_id,
            "description": task["description"],
            "tool": "DBAgent (default)",
            "result": f"SQL:\n{result['sql']}\n\nResult:\n{result['result']}",
            "code_file": None,
        }
    elif pipeline_type == "file":
        result = run_file_agent("sales.csv", task["description"])
        return {
            "task_id": task_id,
            "description": task["description"],
            "tool": "FileAgent (default)",
            "result": result["analysis"],
            "code_file": None,
        }
    else:  # code
        result = run_code_agent(task["description"], task_id=task_id)
        return {
            "task_id": task_id,
            "description": task["description"],
            "tool": "CodeAgent (default)",
            "result": f"Code:\n{result['code']}\n\nOutput:\n{result['output']}",
            "code_file": result.get("code_file"),
        }


def write_code_report_md(tool_results: list[dict], output_md_path: str) -> str:
    """
    Creates a Markdown report listing every CodeAgent task:
    its description, saved .py file path, and execution output.
    Returns the path of the written .md file.
    """
    code_results = [r for r in tool_results if r.get("code_file")]

    lines = [
        "# CodeAgent — Generated Scripts Report\n",
        f"**Total code tasks executed:** {len(code_results)}\n",
    ]

    if not code_results:
        lines.append("_No Python code was generated in this run._\n")
    else:
        for r in code_results:
            lines.append(f"---\n")
            lines.append(f"## Task `{r['task_id']}`\n")
            lines.append(f"**Description:** {r['description']}\n")
            lines.append(f"**Saved script:** `{r['code_file']}`\n")

            # Pull the execution output out of the combined result string
            result_text = r.get("result", "")
            output_section = ""
            if "Output:\n" in result_text:
                output_section = result_text.split("Output:\n", 1)[1].strip()
            lines.append(f"**Execution output:**\n```\n{output_section}\n```\n")

    os.makedirs(os.path.dirname(output_md_path), exist_ok=True)
    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"[Pipeline] Markdown report saved → {output_md_path}")
    return output_md_path


# Main pipeline

def run_day3_pipeline(user_query: str):
    print("\n" + "=" * 60)
    print("MULTI-AGENT PIPELINE — DAY 3 (TOOL-CALLING AGENTS)")
    print("Orchestrator → Tool Agents → Reflection → Validator")
    print("=" * 60)
    print(f"USER QUERY: {user_query}\n")

    # Setup sample data
    init_sample_db()
    create_sample_csv()

    # STEP 1: Plan tasks
    print("─" * 60)
    print("STEP 1 — Orchestrator: Decomposing into subtasks...")
    tasks = plan_tasks(user_query)

    print("\n[Execution Tree]")
    print(f"  Query: \"{user_query}\"")
    for t in tasks:
        print(f"    ├── {t['id']}: {t['description']}")

    # STEP 2: Route each task to the right tool agent
    print(f"\n{'─' * 60}")
    print(f"STEP 2 — Tool Routing: Assigning {len(tasks)} tasks to tool agents...")
    pipeline_type = detect_pipeline_type(user_query)
    print(f"  [Pipeline type detected: {pipeline_type.upper()}]")
    tool_results = []
    for task in tasks:
        result = route_task_to_tool(task, pipeline_type)
        tool_results.append(result)
        print(f"  ✔ {result['task_id']} → {result['tool']} completed")

    # Save generated code files + write .md report
    code_md_path = os.path.join(FILES_DIR, "code_report.md")
    write_code_report_md(tool_results, code_md_path)

    # STEP 3: Reflection
    print(f"\n{'─' * 60}")
    print("STEP 3 — Reflection Agent: Synthesizing tool outputs...")
    improved_answer = run_reflection(user_query, tool_results)

    # STEP 4: Validation loop
    print(f"\n{'─' * 60}")
    print("STEP 4 — Validator: Checking answer quality...")
    final_answer = improved_answer
    validation_result = None

    for attempt in range(1, MAX_RETRIES + 2):
        validation_result = run_validation(user_query, final_answer)

        if validation_result["verdict"] == "PASS":
            print(f"  Validator PASSED on attempt {attempt}")
            break
        else:
            print(f"  Validator FAILED on attempt {attempt}: {validation_result['reason']}")
            if attempt <= MAX_RETRIES:
                print(f"  ↻ Re-running Reflection with feedback...")
                feedback_task = [{
                    "task_id": "feedback",
                    "description": f"Validator feedback: {validation_result['feedback']}",
                    "result": final_answer,
                }]
                final_answer = run_reflection(user_query, tool_results + feedback_task)
            else:
                print(f"  Max retries reached. Using last answer.")

    # RESULTS
    print("\n" + "=" * 60)
    print("PIPELINE RESULTS — DAY 3")
    print("=" * 60)

    print("\n TASK BREAKDOWN:")
    for t in tasks:
        print(f"  [{t['id']}] {t['description']}")

    print("\n TOOL AGENT OUTPUTS:")
    for r in tool_results:
        print(f"\n  [{r['task_id']}] via {r['tool']}")
        print(f"  {r['result'][:300]}{'...' if len(r['result']) > 300 else ''}")

    code_results = [r for r in tool_results if r.get("code_file")]
    if code_results:
        print("\n GENERATED CODE FILES:")
        for r in code_results:
            print(f"  [{r['task_id']}] {r['code_file']}")
        print(f"\n CODE REPORT (Markdown):")
        print(f"  {code_md_path}")

    print(f"\n VALIDATION:")
    print(f"  Verdict : {validation_result['verdict']}")
    print(f"  Reason  : {validation_result['reason']}")

    print(f"\n FINAL ANSWER:\n{final_answer}")
    print("=" * 60)

    # Save final answer to file
    output_filename = "analysis_output.txt"
    write_file(output_filename, final_answer)
    print(f"\n[Output saved to {os.path.join(FILES_DIR, output_filename)}]")

    return {
        "query": user_query,
        "tasks": tasks,
        "tool_results": tool_results,
        "reflection": improved_answer,
        "validation": validation_result,
        "final_answer": final_answer,
        "code_files": [r["code_file"] for r in code_results],
        "code_report_md": code_md_path,
    }


if __name__ == "__main__":
    print("\n MULTI-AGENT SYSTEM — DAY 3")
    print("=" * 60)
    user_input = input("Enter your query: ").strip()
    if not user_input:
        print("No query entered. Using default.")
        user_input = "Analyze sales.csv and generate the top 5 insights about product performance and revenue"
    run_day3_pipeline(user_input)