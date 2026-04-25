import os

TURSO_URL = os.environ.get("TURSO_DATABASE_URL", "")
TURSO_AUTH_TOKEN = os.environ.get("TURSO_AUTH_TOKEN", "")
DB_PATH = os.environ.get("DB_PATH", "./db.sqlite3")

def get_db():
    """Return a DB connection: Turso (cloud) if configured, else local SQLite."""
    if TURSO_URL:
        import libsql_experimental as libsql
        return libsql.connect(TURSO_URL, auth_token=TURSO_AUTH_TOKEN)
    else:
        import sqlite3
        return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS progress (
            user_id INTEGER PRIMARY KEY,
            scene_id TEXT NOT NULL,
            end_id TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()

def get_progress(user_id: int):
    conn = get_db()
    cur = conn.execute("SELECT scene_id, end_id FROM progress WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    if row:
        return {"scene_id": row[0], "end_id": row[1]}
    return None

def save_progress(user_id: int, scene_id: str, end_id: str | None = None):
    conn = get_db()
    conn.execute(
        "INSERT OR REPLACE INTO progress (user_id, scene_id, end_id) VALUES (?, ?, ?)",
        (user_id, scene_id, end_id)
    )
    conn.commit()
