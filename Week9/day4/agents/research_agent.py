import autogen
import os
from dotenv import load_dotenv

load_dotenv()

def get_research_agent():
    config_list = [
        {
            "model": os.getenv("MODEL_NAME", "tinyllama"),
            "base_url": os.getenv("OPENAI_API_BASE", "http://localhost:11434/v1"),
            "api_key": os.getenv("OPENAI_API_KEY", "ollama"),
        }
    ]

    llm_config = {
        "config_list": config_list,
        "temperature": 0.3,
        "max_tokens": 512,
    }

    research_agent = autogen.AssistantAgent(
        name="ResearchAgent",
        system_message="""You are a Research Agent. Your ONLY job is:
- Receive a topic or question from the user
- Gather and present detailed raw facts, data points, and information about the topic
- Do NOT summarize, do NOT give final answers
- Output format: bullet points of raw facts only
- Always end your response with: [RESEARCH COMPLETE - PASS TO SUMMARIZER]
Your role is strictly data gathering. Stay in your lane.""",
        llm_config=llm_config,
        max_consecutive_auto_reply=10,
        human_input_mode="NEVER",
    )

    return research_agent