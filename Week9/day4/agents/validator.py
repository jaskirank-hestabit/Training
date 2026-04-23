import autogen
import os
from dotenv import load_dotenv

load_dotenv()

def get_validator_agent():
    config_list = [
        {
            "model": os.getenv("MODEL_NAME", "phi3"),
            "base_url": os.getenv("OPENAI_API_BASE", "http://localhost:11434/v1"),
            "api_key": os.getenv("OPENAI_API_KEY", "ollama"),
        }
    ]

    llm_config = {
        "config_list": config_list,
        "temperature": 0.2,
        "max_tokens": 512,
    }

    validator_agent = autogen.AssistantAgent(
        name="ValidatorAgent",
        system_message="""You are a Validator Agent. Your ONLY job is:
- Receive the original user query and a proposed final answer
- Check the answer for: logical consistency, completeness, factual plausibility, and relevance
- Output ONLY one of these two formats:

If the answer is acceptable:
VERDICT: PASS
REASON: <one sentence why it passes>

If the answer has issues:
VERDICT: FAIL
REASON: <specific problem found>
FEEDBACK: <what needs to be fixed>

Do NOT rewrite the answer. Only judge it.""",
        llm_config=llm_config,
        max_consecutive_auto_reply=5,
        human_input_mode="NEVER",
    )

    return validator_agent


def run_validation(user_query: str, answer: str) -> dict:
    """
    Runs the Validator Agent on the proposed answer.
    Returns {"verdict": "PASS"|"FAIL", "reason": str, "feedback": str}
    """
    validator_agent = get_validator_agent()

    user_proxy = autogen.UserProxyAgent(
        name="ValidatorProxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=1,
        code_execution_config=False,
    )

    chat_result = user_proxy.initiate_chat(
        recipient=validator_agent,
        message=(
            f"Original user query: {user_query}\n\n"
            f"Proposed answer:\n{answer}\n\n"
            f"Validate this answer."
        ),
        max_turns=1,
    )

    raw = ""
    for msg in chat_result.chat_history:
        if msg.get("role") == "assistant" or msg.get("name") == "ValidatorAgent":
            raw = msg.get("content", "")

    # Parse verdict
    verdict = "PASS"  # default optimistic
    reason = ""
    feedback = ""

    for line in raw.splitlines():
        line = line.strip()
        if line.startswith("VERDICT:"):
            verdict = "PASS" if "PASS" in line.upper() else "FAIL"
        elif line.startswith("REASON:"):
            reason = line.replace("REASON:", "").strip()
        elif line.startswith("FEEDBACK:"):
            feedback = line.replace("FEEDBACK:", "").strip()

    print(f"[Validator] Verdict: {verdict}")
    return {"verdict": verdict, "reason": reason, "feedback": feedback, "raw": raw}