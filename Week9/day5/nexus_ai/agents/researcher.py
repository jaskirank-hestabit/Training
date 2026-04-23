import os
import sys
import autogen

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from nexus_ai.config import get_llm_config
from nexus_ai.utils.logger import NexusLogger
from memory.vector_store import get_vector_store


def get_researcher_agent(memory_context: str = ""):
    system = f"""You are a Research Agent inside NEXUS AI.

Your ONLY job is:
- Receive a query or task
- Provide comprehensive, factual research on the topic
- Cover: background, key concepts, current state, challenges, opportunities
- Use bullet points for clarity
- Be detailed and thorough — this feeds downstream agents
- Do NOT write code, do NOT validate, do NOT summarize

{f"PRIOR MEMORY CONTEXT (use if relevant):\\n{memory_context}" if memory_context else ""}

Always end with: [RESEARCH COMPLETE]"""

    return autogen.AssistantAgent(
        name="ResearcherAgent",
        system_message=system,
        llm_config=get_llm_config(temperature=0.3, max_tokens=1024),
        max_consecutive_auto_reply=3,
        human_input_mode="NEVER",
    )


def run_researcher(user_query: str, plan: dict, session: str = "default") -> str:
    logger = NexusLogger(session)
    vs     = get_vector_store()

    # Memory recall — reuse prior research if available
    similar = vs.search(user_query, top_k=3, session=session)
    memory_context = ""
    if similar:
        memory_context = "\n".join(
            f"  [{m['type']}] {m['text'][:150]}" for m in similar
        )
        logger.log("RESEARCHER", "MEMORY_HIT", f"{len(similar)} similar entries")

    agent = get_researcher_agent(memory_context)

    proxy = autogen.UserProxyAgent(
        name="ResearcherProxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=1,
        code_execution_config=False,
    )

    # Build research tasks from plan
    research_tasks = [
        t["description"] for t in plan.get("tasks", [])
        if t.get("agent") == "Researcher"
    ]
    if not research_tasks:
        research_tasks = [user_query]

    task_str = "\n".join(f"  {i+1}. {t}" for i, t in enumerate(research_tasks))

    chat = proxy.initiate_chat(
        recipient=agent,
        message=(
            f"Research query: {user_query}\n\n"
            f"Specific research tasks:\n{task_str}\n\n"
            "Provide comprehensive research covering all tasks."
        ),
        max_turns=1,
    )

    research = ""
    for msg in chat.chat_history:
        if msg.get("role") == "assistant" or msg.get("name") == "ResearcherAgent":
            research = msg.get("content", "")

    logger.log("RESEARCHER", "DONE", f"{len(research)} chars")
    return research