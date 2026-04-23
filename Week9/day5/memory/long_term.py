import os
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

MEMORY_DIR = os.getenv("MEMORY_DIR", "data/memory")
DB_PATH    = os.path.join(MEMORY_DIR, "long_term.db")


def _get_conn() -> sqlite3.Connection:
    os.makedirs(MEMORY_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # allows dict-like access
    return conn


def init_long_term_db():
    """
    Create the SQLite tables if they don't exist yet.
    Called once at startup.

    Tables:
      conversations  — every message turn (episodic memory)
      facts          — important summarized facts (semantic memory)
    """
    conn = _get_conn()
    cur  = conn.cursor()

    # Episodic: full conversation history
    cur.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            session   TEXT    NOT NULL,
            role      TEXT    NOT NULL,
            agent     TEXT    NOT NULL,
            content   TEXT    NOT NULL,
            ts        TEXT    NOT NULL
        )
    """)

    # Semantic: distilled important facts
    cur.execute("""
        CREATE TABLE IF NOT EXISTS facts (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            session   TEXT    NOT NULL,
            fact      TEXT    NOT NULL,
            source    TEXT    NOT NULL DEFAULT 'agent',
            ts        TEXT    NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    print(f"[LongTermDB] Initialised at {DB_PATH}")


# Episodic memory

def save_conversation_turn(
    session: str,
    role: str,
    agent: str,
    content: str,
) -> int:
    """
    Store one conversation turn.
    Returns the new row ID.
    """
    conn = _get_conn()
    cur  = conn.cursor()
    cur.execute(
        "INSERT INTO conversations (session, role, agent, content, ts) VALUES (?,?,?,?,?)",
        (session, role, agent, content, datetime.utcnow().isoformat()),
    )
    conn.commit()
    row_id = cur.lastrowid
    conn.close()
    return row_id


def get_conversation_history(session: str, limit: int = 20) -> list[dict]:
    """
    Retrieve the last `limit` turns for a session, newest first.
    """
    conn = _get_conn()
    cur  = conn.cursor()
    cur.execute(
        "SELECT * FROM conversations WHERE session=? ORDER BY id DESC LIMIT ?",
        (session, limit),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return list(reversed(rows))   # return oldest-first


def get_all_sessions() -> list[str]:
    """Return all distinct session IDs that have conversation history."""
    conn = _get_conn()
    cur  = conn.cursor()
    cur.execute("SELECT DISTINCT session FROM conversations ORDER BY session")
    sessions = [r[0] for r in cur.fetchall()]
    conn.close()
    return sessions


# Semantic / fact memory

def save_fact(session: str, fact: str, source: str = "agent") -> int:
    """
    Store an important fact distilled from agent output.
    Returns the new row ID.
    """
    conn = _get_conn()
    cur  = conn.cursor()
    cur.execute(
        "INSERT INTO facts (session, fact, source, ts) VALUES (?,?,?,?)",
        (session, fact, source, datetime.utcnow().isoformat()),
    )
    conn.commit()
    row_id = cur.lastrowid
    conn.close()
    return row_id


def get_facts(session: str = None, limit: int = 20) -> list[dict]:
    """
    Retrieve stored facts.
    If session is given, filter by session; otherwise return all.
    """
    conn = _get_conn()
    cur  = conn.cursor()
    if session:
        cur.execute(
            "SELECT * FROM facts WHERE session=? ORDER BY id DESC LIMIT ?",
            (session, limit),
        )
    else:
        cur.execute("SELECT * FROM facts ORDER BY id DESC LIMIT ?", (limit,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def count_conversations() -> int:
    conn = _get_conn()
    cur  = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM conversations")
    n = cur.fetchone()[0]
    conn.close()
    return n


def count_facts() -> int:
    conn = _get_conn()
    cur  = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM facts")
    n = cur.fetchone()[0]
    conn.close()
    return n