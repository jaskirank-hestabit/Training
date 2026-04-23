import autogen
import os
from dotenv import load_dotenv
from agents.research_agent import get_research_agent
from agents.summarizer_agent import get_summarizer_agent
from agents.answer_agent import get_answer_agent

load_dotenv()

def run_agent_pipeline(user_query: str):
    """
    Pipeline:
    User → Research Agent → Summarizer Agent → Answer Agent
    """
    print("\n" + "="*60)
    print("MULTI-AGENT PIPELINE — DAY 1")
    print("="*60)
    print(f"USER QUERY: {user_query}\n")

    # Initialize agents
    research_agent = get_research_agent()
    summarizer_agent = get_summarizer_agent()
    answer_agent = get_answer_agent()

    # Memory window config
    MEMORY_WINDOW = 10

    # STEP 1: User -> Research Agent
    print("\n--- STEP 1: Research Agent gathering facts ---")
    user_proxy = autogen.UserProxyAgent(
        name="User",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=1,
        code_execution_config=False,
    )

    # Initiate research
    chat_result_1 = user_proxy.initiate_chat(
        recipient=research_agent,
        message=f"Research the following topic thoroughly: {user_query}",
        max_turns=1,
    )

    # Extract research output (last message from research agent)
    research_output = ""
    for msg in chat_result_1.chat_history[-MEMORY_WINDOW:]:
        if msg.get("role") == "assistant" or msg.get("name") == "ResearchAgent":
            research_output = msg.get("content", "")

    print(f"\n[Research Output Captured — {len(research_output)} chars]")

    # STEP 2: Research Agent -> Summarizer Agent
    print("\n--- STEP 2: Summarizer Agent condensing facts ---")
    user_proxy_2 = autogen.UserProxyAgent(
        name="ResearchRelay",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=1,
        code_execution_config=False,
    )

    chat_result_2 = user_proxy_2.initiate_chat(
        recipient=summarizer_agent,
        message=f"Here are the raw research facts. Summarize them:\n\n{research_output}",
        max_turns=1,
    )

    # Extract summary output
    summary_output = ""
    for msg in chat_result_2.chat_history[-MEMORY_WINDOW:]:
        if msg.get("role") == "assistant" or msg.get("name") == "SummarizerAgent":
            summary_output = msg.get("content", "")

    print(f"\n[Summary Output Captured — {len(summary_output)} chars]")

    # STEP 3: Summarizer Agent -> Answer Agent 
    print("\n--- STEP 3: Answer Agent crafting final response ---")
    user_proxy_3 = autogen.UserProxyAgent(
        name="SummaryRelay",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=1,
        code_execution_config=False,
    )

    chat_result_3 = user_proxy_3.initiate_chat(
        recipient=answer_agent,
        message=(
            f"Original user question: {user_query}\n\n"
            f"Summary from research:\n{summary_output}\n\n"
            f"Now craft the final user-facing answer."
        ),
        max_turns=1,
    )

    # Extract final answer
    final_answer = ""
    for msg in chat_result_3.chat_history[-MEMORY_WINDOW:]:
        if msg.get("role") == "assistant" or msg.get("name") == "AnswerAgent":
            final_answer = msg.get("content", "")

    # OUTPUT
    print("\n" + "="*60)
    print("PIPELINE RESULTS")
    print("="*60)
    print(f"\n RESEARCH OUTPUT:\n{research_output}")
    print(f"\n SUMMARY:\n{summary_output}")
    print(f"\n FINAL ANSWER:\n{final_answer}")
    print("="*60)

    return {
        "query": user_query,
        "research": research_output,
        "summary": summary_output,
        "final_answer": final_answer,
    }


if __name__ == "__main__":
    print("\n MULTI-AGENT SYSTEM — DAY 1")
    print("="*60)
    user_input = input("Enter your query: ").strip()
    if not user_input:
        print("No query entered. Using default.")
        user_input = "What is the ReAct pattern in AI agents and why is it important?"
    result = run_agent_pipeline(user_input)