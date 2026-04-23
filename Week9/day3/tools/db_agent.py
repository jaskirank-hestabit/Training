import sqlite3
import os
import autogen
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("SQLITE_DB_PATH", "data/sales.db")


def init_sample_db():
    """
    Creates a sample SQLite DB with a sales table if it doesn't exist.
    """
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            revenue REAL NOT NULL,
            region TEXT NOT NULL,
            sale_date TEXT NOT NULL
        )
    """)

    # Insert sample data only if table is empty
    cursor.execute("SELECT COUNT(*) FROM sales")
    if cursor.fetchone()[0] == 0:
        sample_data = [
            ("Laptop Pro", "Electronics", 45, 67500.0, "North", "2024-01-15"),
            ("Wireless Mouse", "Accessories", 200, 6000.0, "South", "2024-01-20"),
            ("USB-C Hub", "Accessories", 150, 7500.0, "East", "2024-02-05"),
            ("Monitor 4K", "Electronics", 30, 27000.0, "North", "2024-02-10"),
            ("Mechanical Keyboard", "Accessories", 80, 12000.0, "West", "2024-02-18"),
            ("Laptop Pro", "Electronics", 60, 90000.0, "South", "2024-03-01"),
            ("Smartphone X", "Electronics", 120, 96000.0, "North", "2024-03-10"),
            ("Tablet Air", "Electronics", 55, 44000.0, "East", "2024-03-15"),
            ("Headphones BT", "Accessories", 95, 14250.0, "West", "2024-03-20"),
            ("Smartwatch S", "Wearables", 70, 35000.0, "South", "2024-04-02"),
            ("Fitness Band", "Wearables", 110, 16500.0, "North", "2024-04-10"),
            ("Webcam HD", "Accessories", 60, 9000.0, "East", "2024-04-15"),
            ("SSD 1TB", "Storage", 85, 25500.0, "West", "2024-04-20"),
            ("External HDD", "Storage", 40, 8000.0, "South", "2024-05-05"),
            ("Router WiFi6", "Networking", 35, 10500.0, "North", "2024-05-12"),
        ]
        cursor.executemany(
            "INSERT INTO sales (product, category, quantity, revenue, region, sale_date) VALUES (?,?,?,?,?,?)",
            sample_data,
        )
        conn.commit()
        print(f"[DB] Sample data inserted into {DB_PATH}")

    conn.close()


def run_sql_query(sql: str) -> str:
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        cols = [desc[0] for desc in cursor.description] if cursor.description else []
        conn.close()

        if not rows:
            return "[DB] Query returned no results."

        # Format as table
        header = " | ".join(cols)
        separator = "-" * len(header)
        lines = [header, separator]
        for row in rows:
            lines.append(" | ".join(str(v) for v in row))

        return "\n".join(lines)
    except Exception as e:
        return f"[DB ERROR] {str(e)}"


def get_db_agent():
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

    db_agent = autogen.AssistantAgent(
        name="DBAgent",
        system_message="""You are a Database Agent. Your ONLY job is:
- Receive a data question about a sales database
- The database has a table called `sales` with columns:
  id, product, category, quantity, revenue, region, sale_date
- Write a valid SQLite SQL query (SELECT only) to answer the question
- Output the SQL in this EXACT format (no extra text):

```sql
SELECT ...
```

- After the SQL block, write: [SQL READY]
- CRITICAL: When using ORDER BY with an alias, always repeat the full expression, not the alias name
  WRONG:  SELECT product, SUM(revenue) AS total_revenue ... ORDER BY total_revenue DESC
  RIGHT:  SELECT product, SUM(revenue) AS total_revenue ... ORDER BY SUM(revenue) DESC
- CRITICAL: Never use spaces in alias names — use underscores (total_revenue not total revenue)
- CRITICAL: Only use column names that exist: id, product, category, quantity, revenue, region, sale_date
- Do NOT explain 
Stay strictly in your lane: write SQL queries only.""",
        llm_config=llm_config,
        max_consecutive_auto_reply=5,
        human_input_mode="NEVER",
    )

    return db_agent


def run_db_agent(question: str) -> dict:
    import re

    # Ensure DB exists with sample data
    init_sample_db()

    agent = get_db_agent()

    user_proxy = autogen.UserProxyAgent(
        name="DBProxy",
        human_input_mode="NEVER",
        max_consecutive_auto_reply=1,
        code_execution_config=False,
    )

    chat_result = user_proxy.initiate_chat(
        recipient=agent,
        message=f"Write a SQL query for this question:\n\n{question}",
        max_turns=1,
    )

    raw = ""
    for msg in chat_result.chat_history:
        if msg.get("role") == "assistant" or msg.get("name") == "DBAgent":
            raw = msg.get("content", "")

    # Extract SQL
    sql_match = re.search(r"```sql\n(.*?)```", raw, re.DOTALL | re.IGNORECASE)
    sql = sql_match.group(1).strip() if sql_match else ""

    if not sql:
        return {
            "question": question,
            "sql": "",
            "result": "[ERROR] No SQL block found in agent response.",
        }

    # Strip any accidental [SQL READY] tags inside the SQL block
    sql = sql.replace("[SQL READY]", "").strip()
    # Remove any trailing semicolons to avoid multi-statement errors
    sql = sql.rstrip(";").strip()

    print(f"[DBAgent] Executing SQL: {sql[:150]}")
    result = run_sql_query(sql)
    print(f"[DBAgent] Result preview: {result[:200]}")

    return {"question": question, "sql": sql, "result": result}