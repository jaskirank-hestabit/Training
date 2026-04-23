import os
import sys
import autogen

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from nexus_ai.config import get_llm_config
from nexus_ai.utils.logger import NexusLogger


def get_analyst_agent(code_context: str = ""):
    extra = f"\nCODE RESULTS:\n{code_context}" if code_context else ""
    return autogen.AssistantAgent(
        name="AnalystAgent",
        system_message=f"""You are an Analyst Agent inside NEXUS AI.

Your ONLY job is:
- Receive research findings and (optionally) code results
- Identify patterns, insights, risks, opportunities
- Produce a structured analysis with:
  1. Key Findings (3-5 bullet points)
  2. Risks & Challenges
  3. Opportunities
  4. Recommended Next Steps
- Be analytical and data-driven, not narrative
- Do NOT write code, do NOT re-research
{extra}

Always end with: [ANALYSIS COMPLETE]""",
        llm_config=get_llm_config(temperature=0.3, max_tokens=1024),
        max_consecutive_auto_reply=3,
        human_input_mode="NEVER",
    )


def run_analyst(
    user_query: str,
    research: str,
    code_result: dict,
    session: str = "default",
) -> str:
    """
    Runs the Analyst agent over research + code results.
    Returns analysis string.
    """
    logger = NexusLogger(session)

    code_context = ""
    if not code_result.get("skipped"):
        code_context = (
            f"Code task: {code_result.get('task', '')}\n"
            f"Output: {code_result.get('output', '')}\n"
        )

    agent = get_analyst_agent(code_context)

    proxy = autogen.UserProxyAgent(
        name="AnalystProxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=1,
        code_execution_config=False,
    )

    chat = proxy.initiate_chat(
        recipient=agent,
        message=(
            f"Original query: {user_query}\n\n"
            f"Research findings:\n{research}\n\n"
            "Provide structured analysis."
        ),
        max_turns=1,
    )

    analysis = ""
    for msg in chat.chat_history:
        if msg.get("role") == "assistant" or msg.get("name") == "AnalystAgent":
            analysis = msg.get("content", "")

    logger.log("ANALYST", "DONE", f"{len(analysis)} chars")
    return analysis