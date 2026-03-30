from src.generator.llm_client import generate_answer


SQL_PROMPT = """
You are a SQL expert.

Given the database schema:

{schema}

Convert the user question into a valid SQLite SQL query.

Rules:
- Only use available tables and columns
- Do NOT hallucinate columns
- Do NOT explain anything
- Return ONLY SQL

Question:
{question}

SQL:
"""


SUMMARY_PROMPT = """
You are a data analyst.

The SQL query executed was:
{sql}

The result of the query is:
{result}

Answer the user's question using ONLY this information.

Rules:
- Do NOT say data is missing if query already filters it
- Trust the SQL result
- Be precise and factual
- Use bullet points if helpful
- Always use alias for aggregates (e.g., SUM(amount) as total_sales)

Question:
{question}

Answer:
"""


def generate_sql(question: str, schema: str) -> str:
    prompt = SQL_PROMPT.format(schema=schema, question=question)
    return generate_answer(prompt).strip()


def summarize_result(question: str, result: str, sql: str) -> str:
    prompt = SUMMARY_PROMPT.format(
        result=result,
        question=question,
        sql=sql
    )
    return generate_answer(prompt).strip()