import autogen
import os
from dotenv import load_dotenv

load_dotenv()

def get_reflection_agent():
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
        "max_tokens": 768,
    }

    reflection_agent = autogen.AssistantAgent(
        name="ReflectionAgent",
        system_message="""You are a Reflection Agent. Your ONLY job is:
- Receive the original user query and multiple worker outputs
- Identify the best result from the worker outputs (ignore errors and failed tasks)
- Synthesize into ONE concise, direct answer that directly answers the user query
- For data/DB queries: lead with the actual data result, then 1-2 sentences of insight
- For code queries: provide the corrected working code block, then a brief explanation
- For analysis queries: bullet the key findings, keep it under 200 words
- CRITICAL: Be concise and direct — do NOT write long narratives or explain errors
- CRITICAL: Always include the actual answer/data/code — not just descriptions of it
- Do NOT validate, do NOT plan new tasks
- Always end with: [REFLECTION COMPLETE]
Your role is strictly synthesis and improvement.""",
        llm_config=llm_config,
        max_consecutive_auto_reply=5,
        human_input_mode="NEVER",
    )

    return reflection_agent


def run_reflection(user_query: str, worker_results: list[dict]) -> str:
    """
    Runs the Reflection Agent over all worker results.
    Returns the improved synthesized answer string.
    """
    reflection_agent = get_reflection_agent()

    # Build combined worker output string
    combined = ""
    for r in worker_results:
        combined += f"\n--- Task {r['task_id']}: {r['description']} ---\n{r['result']}\n"

    user_proxy = autogen.UserProxyAgent(
        name="ReflectionProxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=1,
        code_execution_config=False,
    )

    chat_result = user_proxy.initiate_chat(
        recipient=reflection_agent,
        message=(
            f"Original user query: {user_query}\n\n"
            f"Worker outputs:\n{combined}\n\n"
            f"Synthesize these into one improved comprehensive answer."
        ),
        max_turns=1,
    )

    improved = ""
    for msg in chat_result.chat_history:
        if msg.get("role") == "assistant" or msg.get("name") == "ReflectionAgent":
            improved = msg.get("content", "")

    print(f"[Reflection] Improved answer captured — {len(improved)} chars")
    return improved