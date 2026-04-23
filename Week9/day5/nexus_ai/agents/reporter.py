import os
import sys
import autogen
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from nexus_ai.config import get_llm_config
from nexus_ai.utils.logger import NexusLogger


def get_reporter_agent():
    return autogen.AssistantAgent(
        name="ReporterAgent",
        system_message="""You are a Reporter Agent inside NEXUS AI.

Your ONLY job is to produce the FINAL, COMPLETE output the user asked for.

CRITICAL RULES:
- Read the original query carefully and match the output format to what was asked
- If the user asked for structured content (plan, list, breakdown, schedule):
  → Output the FULL structure with ALL sections/items — do not summarize or truncate
  → Use the same level of detail the user requested
- If the user asked for a report or analysis:
  → Use: Executive Summary, Key Findings, Detailed Analysis, Recommendations, Next Steps
- Be EXHAUSTIVE — never abbreviate or skip sections
- Do NOT include internal agent markers like [RESEARCH COMPLETE] or [ANALYSIS COMPLETE]

FORMATTING (terminal-friendly):
- Use separators (===), section headers, and bullet points for clarity
- Keep formatting clean and readable in a terminal
- Match the structure and granularity the user explicitly requested

Always end with: [REPORT DELIVERED]""",
        llm_config=get_llm_config(temperature=0.5, max_tokens=4096),
        max_consecutive_auto_reply=3,
        human_input_mode="NEVER",
    )


def run_reporter(
    user_query: str,
    results: dict,
    session: str = "default",
) -> str:
    logger = NexusLogger(session)
    agent  = get_reporter_agent()

    proxy = autogen.UserProxyAgent(
        name="ReporterProxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=1,
        code_execution_config=False,
    )

    optimized = results.get("optimized", "")
    analysis  = results.get("analysis", "")
    research  = results.get("research", "")

    code_res = results.get("code_result", {})
    code_section = ""
    if not code_res.get("skipped"):
        code_section = (
            f"\nCode Results:\n"
            f"  Task: {code_res.get('task', '')}\n"
            f"  Output: {code_res.get('output', '')}\n"
            f"  Files: {code_res.get('py_path', 'N/A')}\n"
        )

    plan = results.get("plan", {})
    goal = plan.get("goal", user_query) if isinstance(plan, dict) else user_query

    chat = proxy.initiate_chat(
        recipient=agent,
        message=(
            f"Original Query: {user_query}\n"
            f"Goal: {goal}\n\n"
            f"Research Findings:\n{research}\n\n"
            f"Optimized Answer:\n{optimized}\n\n"
            f"Analysis:\n{analysis}\n"
            f"{code_section}\n"
            "Generate the complete final output exactly as the user requested."
        ),
        max_turns=1,
    )

    report = ""
    for msg in chat.chat_history:
        if msg.get("role") == "assistant" or msg.get("name") == "ReporterAgent":
            report = msg.get("content", "")

    report = re.sub(r"\[.*?COMPLETE\]", "", report).strip()
    report = re.sub(r"\[REPORT DELIVERED\]", "", report).strip()

    logger.log("REPORTER", "DONE", f"{len(report)} chars")
    return report