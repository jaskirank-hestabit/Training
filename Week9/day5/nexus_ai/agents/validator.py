import os
import sys
import autogen

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from nexus_ai.config import get_llm_config
from nexus_ai.utils.logger import NexusLogger


def get_nexus_validator_agent():
    return autogen.AssistantAgent(
        name="NexusValidatorAgent",
        system_message="""You are a Validator Agent inside NEXUS AI.

Your ONLY job is to validate the final answer against these criteria:
1. Does it directly answer the original query?
2. Is it logically consistent (no contradictions)?
3. Is it complete (covers main aspects)?
4. Is it factually plausible?
5. Is it well-structured and clear?

Output EXACTLY one of these formats:

VERDICT: PASS
REASON: <one sentence why it passes>

OR

VERDICT: FAIL
REASON: <specific problem>
FEEDBACK: <what to fix>

Nothing else. No extra commentary.""",
        llm_config=get_llm_config(temperature=0.1),
        max_consecutive_auto_reply=3,
        human_input_mode="NEVER",
    )


def run_nexus_validator(
    user_query: str,
    answer: str,
    session: str = "default",
) -> dict:
    """
    Runs the NEXUS Validator. Returns {"verdict", "reason", "feedback", "raw"}.
    """
    logger = NexusLogger(session)
    agent  = get_nexus_validator_agent()

    proxy = autogen.UserProxyAgent(
        name="NexusValidatorProxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=1,
        code_execution_config=False,
    )

    chat = proxy.initiate_chat(
        recipient=agent,
        message=(
            f"Original query: {user_query}\n\n"
            f"Final answer:\n{answer}\n\n"
            "Validate."
        ),
        max_turns=1,
    )

    raw = ""
    for msg in chat.chat_history:
        if msg.get("role") == "assistant" or msg.get("name") == "NexusValidatorAgent":
            raw = msg.get("content", "")

    verdict  = "PASS"
    reason   = "Answer meets quality criteria"
    feedback = ""

    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("VERDICT:"):
            verdict = "PASS" if "PASS" in line.upper() else "FAIL"
        elif line.startswith("REASON:"):
            reason = line.replace("REASON:", "").strip()
        elif line.startswith("FEEDBACK:"):
            feedback = line.replace("FEEDBACK:", "").strip()

    logger.log("VALIDATOR", verdict, reason)
    return {"verdict": verdict, "reason": reason, "feedback": feedback, "raw": raw}