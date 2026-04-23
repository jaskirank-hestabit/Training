import autogen
import os
from dotenv import load_dotenv

load_dotenv()

def get_summarizer_agent():
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

    summarizer_agent = autogen.AssistantAgent(
        name="SummarizerAgent",
        system_message="""You are a Summarizer Agent. Your ONLY job is:
- Receive raw research facts/bullet points
- Condense them into a clean, concise summary (3-5 sentences max)
- Remove redundancy, keep only the most important points
- Do NOT answer questions, do NOT add new information
- Output format: A short paragraph summary only
- Always end your response with: [SUMMARY COMPLETE - PASS TO ANSWER AGENT]
Your role is strictly condensing information.""",
        llm_config=llm_config,
        max_consecutive_auto_reply=10,
        human_input_mode="NEVER",
    )

    return summarizer_agent