import os
import csv
import autogen
from dotenv import load_dotenv

load_dotenv()

FILES_DIR = os.getenv("FILES_DIR", "data/files")


def ensure_files_dir():
    os.makedirs(FILES_DIR, exist_ok=True)


def read_file(filename: str) -> str:
    """Reads a .txt or .csv file from FILES_DIR."""
    ensure_files_dir()
    path = os.path.join(FILES_DIR, filename)

    if not os.path.exists(path):
        return f"[ERROR] File not found: {filename}"

    ext = os.path.splitext(filename)[1].lower()

    try:
        if ext == ".csv":
            rows = []
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    rows.append(", ".join(row))
            return "\n".join(rows)
        else:
            with open(path, encoding="utf-8") as f:
                return f.read()
    except Exception as e:
        return f"[ERROR] Could not read file: {str(e)}"


def write_file(filename: str, content: str) -> str:
    """Writes content to a .txt or .csv file in FILES_DIR."""
    ensure_files_dir()
    path = os.path.join(FILES_DIR, filename)

    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"[OK] Written to {path} ({len(content)} chars)"
    except Exception as e:
        return f"[ERROR] Could not write file: {str(e)}"


def list_files() -> str:
    """Lists all files in FILES_DIR."""
    ensure_files_dir()
    files = os.listdir(FILES_DIR)
    return "\n".join(files) if files else "[No files found]"


def create_sample_csv():
    """Creates a sample sales.csv in FILES_DIR for testing."""
    ensure_files_dir()
    path = os.path.join(FILES_DIR, "sales.csv")
    if not os.path.exists(path):
        rows = [
            ["product", "category", "quantity", "revenue", "region"],
            ["Laptop Pro", "Electronics", "45", "67500", "North"],
            ["Wireless Mouse", "Accessories", "200", "6000", "South"],
            ["USB-C Hub", "Accessories", "150", "7500", "East"],
            ["Monitor 4K", "Electronics", "30", "27000", "North"],
            ["Mechanical Keyboard", "Accessories", "80", "12000", "West"],
            ["Smartphone X", "Electronics", "120", "96000", "North"],
            ["Tablet Air", "Electronics", "55", "44000", "East"],
            ["Headphones BT", "Accessories", "95", "14250", "West"],
            ["Smartwatch S", "Wearables", "70", "35000", "South"],
            ["Fitness Band", "Wearables", "110", "16500", "North"],
        ]
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        print(f"[FileAgent] Sample sales.csv created at {path}")


def get_file_agent():
    config_list = [
        {
            "model": os.getenv("MODEL_NAME", "phi3"),
            "base_url": os.getenv("OPENAI_API_BASE", "http://localhost:11434/v1"),
            "api_key": os.getenv("OPENAI_API_KEY", "ollama"),
        }
    ]

    llm_config = {
        "config_list": config_list,
        "temperature": 0.3,
        "max_tokens": 768,
    }

    file_agent = autogen.AssistantAgent(
        name="FileAgent",
        system_message="""You are a File Analysis Agent. Your ONLY job is:
- Receive raw CSV or text file content
- Analyze the data and extract meaningful insights
- Output a clean analysis with:
  1. Summary of the data (rows, columns, types)
  2. Key statistics (totals, averages, min/max where relevant)
  3. Top 5 insights or patterns found
- Format as numbered points, be concise and factual
- Always end with: [FILE ANALYSIS COMPLETE]
Do NOT read or write files yourself. Only analyze data given to you.""",
        llm_config=llm_config,
        max_consecutive_auto_reply=5,
        human_input_mode="NEVER",
    )

    return file_agent


def run_file_agent(filename: str, task: str = "analyze") -> dict:
    # Read file content
    content = read_file(filename)

    if content.startswith("[ERROR]"):
        return {"filename": filename, "content_preview": "", "analysis": content}

    agent = get_file_agent()

    user_proxy = autogen.UserProxyAgent(
        name="FileProxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=1,
        code_execution_config=False,
    )

    chat_result = user_proxy.initiate_chat(
        recipient=agent,
        message=(
            f"Task: {task}\n\n"
            f"File: {filename}\n\n"
            f"Content:\n{content}"
        ),
        max_turns=1,
    )

    analysis = ""
    for msg in chat_result.chat_history:
        if msg.get("role") == "assistant" or msg.get("name") == "FileAgent":
            analysis = msg.get("content", "")

    print(f"[FileAgent] Analysis captured — {len(analysis)} chars")
    return {
        "filename": filename,
        "content_preview": content[:300],
        "analysis": analysis,
    }