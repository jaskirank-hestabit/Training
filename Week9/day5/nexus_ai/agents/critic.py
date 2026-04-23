import os
import sys
import autogen

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from nexus_ai.config import get_llm_config
from nexus_ai.utils.logger import NexusLogger


def get_critic_agent():
    return autogen.AssistantAgent(
        name="CriticAgent",
        system_message="""You are a Critic Agent inside NEXUS AI.

Your ONLY job is:
- Receive an analysis/answer draft
- Critically evaluate it for:
  * Missing information or gaps
  * Logical errors or contradictions
  * Unsupported claims
  * Lack of specificity
  * Bias or one-sidedness
- Output a structured critique:

STRENGTHS:
- [what's good]

WEAKNESSES / GAPS:
- [what's missing or wrong]

IMPROVEMENT SUGGESTIONS:
- [specific things to fix]

CONFIDENCE SCORE: X/10

Always end with: [CRITIQUE COMPLETE]""",
        llm_config=get_llm_config(temperature=0.3),
        max_consecutive_auto_reply=3,
        human_input_mode="NEVER",
    )


def run_critic(user_query: str, analysis: str, session: str = "default") -> str:
    """
    Runs the Critic agent. Returns critique string.
    """
    logger = NexusLogger(session)
    agent  = get_critic_agent()

    proxy = autogen.UserProxyAgent(
        name="CriticProxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=1,
        code_execution_config=False,
    )

    chat = proxy.initiate_chat(
        recipient=agent,
        message=(
            f"Original query: {user_query}\n\n"
            f"Draft analysis:\n{analysis}\n\n"
            "Provide a critical evaluation."
        ),
        max_turns=1,
    )

    critique = ""
    for msg in chat.chat_history:
        if msg.get("role") == "assistant" or msg.get("name") == "CriticAgent":
            critique = msg.get("content", "")

    logger.log("CRITIC", "DONE", f"{len(critique)} chars")
    return critique