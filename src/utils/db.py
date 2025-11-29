#src/utils/db.py
import sqlite3
from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger("DB")

def get_connection():
    return sqlite3.connect(settings.DB_FILE)

def initialize_db():
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT
        )
        """)

        conn.commit()
        conn.close()
        logger.info("SQLite database initialized")
    except Exception as e:
        logger.error(f"DB Error: {e}")
