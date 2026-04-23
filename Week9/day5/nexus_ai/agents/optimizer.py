import os
import sys
import autogen

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from nexus_ai.config import get_llm_config
from nexus_ai.utils.logger import NexusLogger


def get_optimizer_agent():
    return autogen.AssistantAgent(
        name="OptimizerAgent",
        system_message="""You are an Optimizer Agent inside NEXUS AI.

Your ONLY job is:
- Receive a draft analysis AND a critique of it
- Improve the analysis by:
  * Addressing all weaknesses/gaps identified by the Critic
  * Adding missing information
  * Fixing logical errors
  * Making claims more specific and supported
  * Removing bias
- Output ONLY the improved, final-quality answer
- Structure it clearly with headers and bullet points
- Be comprehensive but concise

Always end with: [OPTIMIZATION COMPLETE]""",
        llm_config=get_llm_config(temperature=0.4, max_tokens=1024),
        max_consecutive_auto_reply=3,
        human_input_mode="NEVER",
    )


def run_optimizer(
    user_query: str,
    analysis: str,
    critique: str,
    session: str = "default",
) -> str:
    """
    Runs the Optimizer agent. Returns improved answer string.
    """
    logger = NexusLogger(session)
    agent  = get_optimizer_agent()

    proxy = autogen.UserProxyAgent(
        name="OptimizerProxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=1,
        code_execution_config=False,
    )

    chat = proxy.initiate_chat(
        recipient=agent,
        message=(
            f"Original query: {user_query}\n\n"
            f"Draft analysis:\n{analysis}\n\n"
            f"Critique:\n{critique}\n\n"
            "Produce an improved, comprehensive final answer."
        ),
        max_turns=1,
    )

    optimized = ""
    for msg in chat.chat_history:
        if msg.get("role") == "assistant" or msg.get("name") == "OptimizerAgent":
            optimized = msg.get("content", "")

    logger.log("OPTIMIZER", "DONE", f"{len(optimized)} chars")
    return optimized