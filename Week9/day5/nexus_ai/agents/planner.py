import os
import json
import autogen
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from nexus_ai.config import get_llm_config
from nexus_ai.utils.logger import NexusLogger


def get_planner_agent():
    planner = autogen.AssistantAgent(
        name="PlannerAgent",
        system_message="""You are a Strategic Planner Agent inside NEXUS AI.

Your ONLY job is:
- Receive a user query
- Break it into 3-5 concrete, ordered tasks
- Assign each task to one of: Researcher, Analyst
  (NEVER assign "Coder" unless the user explicitly asks for code, a script, or a program)
- Identify if code execution or data analysis is needed
- Output ONLY valid JSON — no markdown, no extra text

IMPORTANT RULES:
- "needs_code" must be true ONLY if the user says "write code", "implement", "script", "program", or asks for executable output
- Roadmaps, plans, curricula, reports, strategies → needs_code: false, no Coder tasks
- Do NOT assign Coder for content generation, writing, planning, or analysis tasks

Output format EXACTLY:
{
  "goal": "<one-line goal>",
  "tasks": [
    {"id": "task_1", "description": "<what to do>", "agent": "Researcher|Analyst", "priority": 1},
    {"id": "task_2", "description": "<what to do>", "agent": "Researcher|Analyst", "priority": 2}
  ],
  "needs_code": false,
  "needs_data": true|false,
  "complexity": "low|medium|high"
}

Always end with: [PLAN READY]""",
        llm_config=get_llm_config(temperature=0.2),
        max_consecutive_auto_reply=3,
        human_input_mode="NEVER",
    )
    return planner


def run_planner(user_query: str, session: str = "default") -> dict:
    logger = NexusLogger(session)
    agent  = get_planner_agent()

    proxy = autogen.UserProxyAgent(
        name="PlannerProxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=1,
        code_execution_config=False,
    )

    chat = proxy.initiate_chat(
        recipient=agent,
        message=f"Create a strategic plan for this query:\n\n{user_query}",
        max_turns=1,
    )

    raw = ""
    for msg in chat.chat_history:
        if msg.get("role") == "assistant" or msg.get("name") == "PlannerAgent":
            raw = msg.get("content", "")

    # Parse JSON
    try:
        clean = raw.replace("[PLAN READY]", "").strip()
        if "```" in clean:
            import re
            m = re.search(r"```(?:json)?\n(.*?)```", clean, re.DOTALL)
            if m:
                clean = m.group(1).strip()
        start = clean.find("{")
        end   = clean.rfind("}") + 1
        if start != -1 and end > start:
            plan = json.loads(clean[start:end])
            # Safety override: never force code for non-code queries
            code_keywords = ["write code", "implement", "script", "program", "function", "algorithm"]
            query_lower = user_query.lower()
            if not any(kw in query_lower for kw in code_keywords):
                plan["needs_code"] = False
                plan["tasks"] = [t for t in plan.get("tasks", []) if t.get("agent") != "Coder"]
            logger.log("PLANNER", "OK", f"{len(plan.get('tasks', []))} tasks")
            return plan
    except Exception as e:
        logger.log("PLANNER", "PARSE_FAIL", str(e))

    # Fallback plan
    return {
        "goal": user_query,
        "tasks": [
            {"id": "task_1", "description": f"Research: {user_query}", "agent": "Researcher", "priority": 1},
            {"id": "task_2", "description": f"Analyse findings for: {user_query}", "agent": "Analyst", "priority": 2},
        ],
        "needs_code": False,
        "needs_data": False,
        "complexity": "medium",
    }