import autogen
import os
from dotenv import load_dotenv

load_dotenv()

def get_answer_agent():
    config_list = [
        {
            "model": os.getenv("MODEL_NAME", "tinyllama"),
            "base_url": os.getenv("OPENAI_API_BASE", "http://localhost:11434/v1"),
            "api_key": os.getenv("OPENAI_API_KEY", "ollama"),
        }
    ]

    llm_config = {
        "config_list": config_list,
        "temperature": 0.5,
        "max_tokens": 512,
    }

    answer_agent = autogen.AssistantAgent(
        name="AnswerAgent",
        system_message="""You are an Answer Agent. Your ONLY job is:
- Receive a condensed summary from the Summarizer Agent
- Formulate a clear, direct, user-friendly final answer
- The answer must be conversational and directly address the original user question
- Do NOT do research, do NOT summarize raw data
- Output format: A friendly, complete final answer paragraph
- Always end with: [FINAL ANSWER DELIVERED]
Your role is strictly crafting the final user-facing response. Stay in your lane.""",
        llm_config=llm_config,
        max_consecutive_auto_reply=10,
        human_input_mode="NEVER",
    )

    return answer_agent