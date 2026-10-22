"""SQLite storage for subscribers -- deliberately simple for a demo/prototype."""
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "subscribers.db")


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _connect()
    conn.execute(
        """CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            zip_code TEXT,
            grocery_list TEXT NOT NULL,
            stores TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )"""
    )
    conn.commit()
    conn.close()


def add_subscriber(email: str, zip_code: str, grocery_list: list, stores: list):
    conn = _connect()
    conn.execute(
        """INSERT INTO subscribers (email, zip_code, grocery_list, stores)
           VALUES (?, ?, ?, ?)
           ON CONFLICT(email) DO UPDATE SET
             zip_code=excluded.zip_code,
             grocery_list=excluded.grocery_list,
             stores=excluded.stores""",
        (email, zip_code, ",".join(grocery_list), ",".join(stores)),
    )
    conn.commit()
    conn.close()


def get_all_subscribers():
    conn = _connect()
    rows = conn.execute("SELECT * FROM subscribers ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]
