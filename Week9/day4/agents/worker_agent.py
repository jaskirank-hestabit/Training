import autogen
import os
from dotenv import load_dotenv

load_dotenv()

def get_worker_agent(worker_id: str):
    config_list = [
        {
            "model": os.getenv("MODEL_NAME", "phi3"),
            "base_url": os.getenv("OPENAI_API_BASE", "http://localhost:11434/v1"),
            "api_key": os.getenv("OPENAI_API_KEY", "ollama"),
        }
    ]

    llm_config = {
        "config_list": config_list,
        "temperature": 0.4,
        "max_tokens": 512,
    }

    worker = autogen.AssistantAgent(
        name=f"WorkerAgent_{worker_id}",
        system_message=f"""You are Worker Agent {worker_id}. Your ONLY job is:
- Receive a single assigned subtask
- Research and reason about ONLY that subtask
- Produce a detailed, factual response covering that subtask fully
- Do NOT answer other subtasks, do NOT summarize, do NOT validate
- Output format: A focused response with clear bullet points or short paragraphs
- Always end with: [WORKER {worker_id} COMPLETE]
Stay strictly within your assigned task scope.""",
        llm_config=llm_config,
        max_consecutive_auto_reply=5,
        human_input_mode="NEVER",
    )

    return worker


def run_worker_task(task: dict) -> dict:
    """
    Runs a single worker agent on its assigned task.
    Returns {"task_id": ..., "description": ..., "result": ...}
    """
    task_id = task.get("id", "task_unknown")
    description = task.get("description", "")

    worker = get_worker_agent(task_id)

    user_proxy = autogen.UserProxyAgent(
        name=f"WorkerProxy_{task_id}",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=1,
        code_execution_config=False,
    )

    chat_result = user_proxy.initiate_chat(
        recipient=worker,
        message=f"Your assigned subtask is:\n\n{description}\n\nExecute this task fully.",
        max_turns=1,
    )

    result = ""
    for msg in chat_result.chat_history:
        if msg.get("role") == "assistant" or f"WorkerAgent_{task_id}" in msg.get("name", ""):
            result = msg.get("content", "")

    print(f"[Worker {task_id}] Done — {len(result)} chars")
    return {"task_id": task_id, "description": description, "result": result}