import autogen
import os
import json
from dotenv import load_dotenv

load_dotenv()

def get_llm_config():
    return {
        "config_list": [
            {
                "model": os.getenv("MODEL_NAME", "phi3"),
                "base_url": os.getenv("OPENAI_API_BASE", "http://localhost:11434/v1"),
                "api_key": os.getenv("OPENAI_API_KEY", "ollama"),
            }
        ],
        "temperature": 0.3,
        "max_tokens": 512,
    }


def get_orchestrator_agent():
    orchestrator = autogen.AssistantAgent(
        name="OrchestratorAgent",
        system_message="""You are an Orchestrator / Planner Agent. Your ONLY job is:
- Receive a user query
- Break it into 2 to 3 clear, independent subtasks that can be worked on in parallel
- Each subtask must be self-contained (no subtask depends on another)
- Output ONLY a valid JSON array, no extra text, no markdown fences
- Format exactly:
[
  {"id": "task_1", "description": "..."},
  {"id": "task_2", "description": "..."},
  {"id": "task_3", "description": "..."}
]
Do NOT answer the query. Only decompose it into subtasks.""",
        llm_config=get_llm_config(),
        max_consecutive_auto_reply=5,
        human_input_mode="NEVER",
    )
    return orchestrator


def plan_tasks(user_query: str) -> list[dict]:
    orchestrator = get_orchestrator_agent()

    user_proxy = autogen.UserProxyAgent(
        name="PlannerProxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=1,
        code_execution_config=False,
    )

    chat_result = user_proxy.initiate_chat(
        recipient=orchestrator,
        message=f"Decompose this query into 2-3 independent parallel subtasks:\n\n{user_query}",
        max_turns=1,
    )

    # Extract the assistant's last reply
    raw_output = ""
    for msg in chat_result.chat_history:
        if msg.get("role") == "assistant" or msg.get("name") == "OrchestratorAgent":
            raw_output = msg.get("content", "")

    # Try to parse JSON
    try:
        # Strip any accidental markdown fences
        clean = raw_output.strip()
        if clean.startswith("```"):
            clean = "\n".join(clean.split("\n")[1:])
        if clean.endswith("```"):
            clean = "\n".join(clean.split("\n")[:-1])
        tasks = json.loads(clean.strip())
        if isinstance(tasks, list) and len(tasks) > 0:
            print(f"[Orchestrator] Planned {len(tasks)} tasks.")
            return tasks
    except Exception as e:
        print(f"[Orchestrator] JSON parse failed: {e}. Falling back to single task.")

    # Fallback: single task
    return [{"id": "task_1", "description": user_query}]