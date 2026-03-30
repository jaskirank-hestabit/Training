import sqlite3


def load_schema(db_path: str) -> str:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    tables = cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    ).fetchall()

    schema_str = ""

    for (table_name,) in tables:
        schema_str += f"\nTable: {table_name}\n"

        columns = cursor.execute(f"PRAGMA table_info({table_name});").fetchall()

        for col in columns:
            col_name = col[1]
            col_type = col[2]
            schema_str += f"  - {col_name} ({col_type})\n"

    conn.close()
    return schema_str.strip()