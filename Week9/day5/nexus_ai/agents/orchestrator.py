import os
import sys
import autogen

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from nexus_ai.config import get_llm_config
from nexus_ai.utils.logger import NexusLogger


def get_orchestrator_agent():
    orc = autogen.AssistantAgent(
        name="NexusOrchestrator",
        system_message="""You are the Master Orchestrator of NEXUS AI.

Your ONLY job is:
- Receive a user query and a structured plan
- Decide which agents are needed and in what order
- Produce a clear execution directive that other agents can follow
- Identify parallelism opportunities (tasks that can run at same time)
- Handle failure recovery: if a task fails, suggest an alternative

Output format:
EXECUTION DIRECTIVE:
[Ordered list of agents and their tasks]

PARALLELISM:
[Which tasks can run in parallel]

FAILURE RECOVERY:
[Fallback strategies]

Always end with: [ORCHESTRATION COMPLETE]""",
        llm_config=get_llm_config(temperature=0.3),
        max_consecutive_auto_reply=3,
        human_input_mode="NEVER",
    )
    return orc


def run_orchestrator(user_query: str, plan: dict, session: str = "default") -> dict:
    logger = NexusLogger(session)
    agent  = get_orchestrator_agent()

    proxy = autogen.UserProxyAgent(
        name="OrchestratorProxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=1,
        code_execution_config=False,
    )

    tasks_str = "\n".join(
        f"  - [{t['id']}] ({t.get('agent','?')}) {t['description']}"
        for t in plan.get("tasks", [])
    )

    chat = proxy.initiate_chat(
        recipient=agent,
        message=(
            f"User Query: {user_query}\n\n"
            f"Planned Tasks:\n{tasks_str}\n\n"
            f"Complexity: {plan.get('complexity', 'medium')}\n"
            f"Needs code: {plan.get('needs_code', False)}\n"
            f"Needs data: {plan.get('needs_data', False)}\n\n"
            "Create execution directive."
        ),
        max_turns=1,
    )

    directive = ""
    for msg in chat.chat_history:
        if msg.get("role") == "assistant" or msg.get("name") == "NexusOrchestrator":
            directive = msg.get("content", "")

    logger.log("ORCHESTRATOR", "DIRECTIVE", directive[:200])
    return {
        "directive": directive,
        "tasks":     plan.get("tasks", []),
        "plan":      plan,
    }