import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "memory.db"


def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)
def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS session_files (
            session_id TEXT PRIMARY KEY,
            uploaded_file TEXT,
            file_type TEXT,
            schema TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

def init_history_table():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cur = conn.cursor()

    cur.execute("""
        DROP TABLE IF EXISTS session_history
    """)

    cur.execute("""
        CREATE TABLE session_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            query TEXT,
            answer TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)


    conn.commit()
    conn.close()


def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def save_session_file_state(state):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO session_files (session_id, uploaded_file, file_type, schema)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(session_id) DO UPDATE SET
            uploaded_file = excluded.uploaded_file,
            file_type = excluded.file_type,
            schema = excluded.schema,
            updated_at = CURRENT_TIMESTAMP
    """, (
        state.get("session_id"),
        state.get("uploaded_file"),
        state.get("file_type"),
        state.get("schema")
    ))

    conn.commit()
    conn.close()


def load_session_file_state(session_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT uploaded_file, file_type, schema
        FROM session_files
        WHERE session_id = ?
    """, (session_id,))

    row = cur.fetchone()
    conn.close()

    if not row:
        return {}

    return {
        "uploaded_file": row[0],
        "file_type": row[1],
        "schema": row[2]
    }

def save_history(session_id, query, answer):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO session_history (session_id, query, answer)
        VALUES (?, ?, ?)
    """, (session_id, query, answer))

    conn.commit()
    conn.close()

def load_last_two_messages(session_id):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT query, answer
        FROM session_history
        WHERE session_id = ?
        ORDER BY id DESC
        LIMIT 2
    """, (session_id,))

    rows = cur.fetchall()
    conn.close()

    # reverse so oldest → newest
    rows.reverse()

    return [
        {"query": q, "answer": a}
        for q, a in rows
    ]
