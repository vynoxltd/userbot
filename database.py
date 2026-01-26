# database.py
import sqlite3

DB_PATH = "data.db"

def _connect():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

db = _connect()
cur = db.cursor()

# ---------- TABLES ----------

cur.execute("""
CREATE TABLE IF NOT EXISTS notes (
    key TEXT PRIMARY KEY,
    value TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS settings (
    name TEXT PRIMARY KEY,
    value INTEGER
)
""")

db.commit()

# ---------- NOTES ----------

def set_note(key, value):
    cur.execute(
        "REPLACE INTO notes VALUES (?, ?)",
        (key, value)
    )
    db.commit()

def get_note(key):
    cur.execute(
        "SELECT value FROM notes WHERE key=?",
        (key,)
    )
    row = cur.fetchone()
    return row[0] if row else None

def del_note(key):
    cur.execute(
        "DELETE FROM notes WHERE key=?",
        (key,)
    )
    db.commit()

# ---------- SETTINGS ----------

def set_setting(name, value: bool):
    cur.execute(
        "REPLACE INTO settings VALUES (?, ?)",
        (name, int(value))
    )
    db.commit()

def get_setting(name):
    cur.execute(
        "SELECT value FROM settings WHERE name=?",
        (name,)
    )
    row = cur.fetchone()
    return bool(row[0]) if row else False