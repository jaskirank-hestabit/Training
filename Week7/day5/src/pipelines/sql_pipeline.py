import sqlite3
import re

from src.generator.sql_generator import generate_sql, summarize_result
from src.utils.schema_loader import load_schema


DB_PATH = "src/data/raw/sample.db"


# ---------- SQL VALIDATOR ----------
def is_safe_sql(query: str) -> bool:
    query = query.lower()

    forbidden = ["drop", "delete", "insert", "update", "alter"]
    return not any(word in query for word in forbidden)


# ---------- CLEAN SQL ----------
def clean_sql(sql: str) -> str:
    # remove ```sql ``` if LLM adds it
    sql = re.sub(r"```sql|```", "", sql, flags=re.IGNORECASE).strip()
    return sql


# ---------- EXECUTE ----------
def execute_sql(query: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        cols = [desc[0] for desc in cursor.description]

        result = []
        for row in rows:
            result.append(dict(zip(cols, row)))

        return result

    except Exception as e:
        return f"ERROR: {str(e)}"

    finally:
        conn.close()


# ---------- MAIN PIPELINE ----------
def run_sql_pipeline(question: str):
    print("\n=== SQL PIPELINE ===\n")

    # 1. Load schema
    schema = load_schema(DB_PATH)
    print("Schema:\n", schema)

    # 2. Generate SQL
    sql = generate_sql(question, schema)
    sql = clean_sql(sql)

    print("\nGenerated SQL:\n", sql)

    # 3. Validate
    if not is_safe_sql(sql):
        return {
            "error": "Unsafe SQL detected!",
            "sql": sql
        }

    # 4. Execute
    result = execute_sql(sql)

    if isinstance(result, str) and result.startswith("ERROR"):
        return {
            "error": result,
            "sql": sql
        }

    print("\nRaw Result:\n", result[:5])

    # 5. Summarize
    summary = summarize_result(question, str(result), sql)

    return {
        "sql": sql,
        "result": result,
        "answer": summary
    }


if __name__ == "__main__":
    q = input("Ask SQL question: ")
    out = run_sql_pipeline(q)

    print("\n=== FINAL ANSWER ===\n")
    print(out.get("answer", out.get("error")))