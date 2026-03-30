import sqlite3
import os

DB_PATH = "src/data/raw/sample.db"

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Create table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY,
        artist TEXT,
        year INTEGER,
        amount INTEGER
    )
    """)

    # Optional: clear old data (so reruns don't duplicate)
    cur.execute("DELETE FROM sales")

    # Insert data
    data = [
        ("Adele", 2023, 5000),
        ("Drake", 2023, 7000),
        ("Adele", 2022, 4000),
    ]

    cur.executemany(
        "INSERT INTO sales (artist, year, amount) VALUES (?, ?, ?)",
        data
    )

    conn.commit()
    conn.close()

    print(f"Database initialized at {DB_PATH}")


if __name__ == "__main__":
    init_db()