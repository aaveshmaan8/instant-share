import sqlite3
from config import DATABASE_PATH


# ================= GET CONNECTION =================
def get_connection():
    conn = sqlite3.connect(DATABASE_PATH, timeout=10)
    conn.row_factory = sqlite3.Row

    # Performance & safety settings
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = NORMAL")

    return conn


# ================= INITIALIZE DATABASE =================
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            filename TEXT NOT NULL,
            original_name TEXT NOT NULL,
            upload_time INTEGER NOT NULL,
            expires_at INTEGER NOT NULL,
            downloads INTEGER DEFAULT 0,
            created_date TEXT NOT NULL,
            uploader_ip TEXT,
            downloader_ip TEXT,
            file_size INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


# ================= CLEANUP EXPIRED FILES (DB ONLY) =================
def cleanup_expired_files(current_time):
    """
    Deletes expired DB records.
    File deletion handled in file_service.
    """
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            "DELETE FROM files WHERE expires_at < ?",
            (current_time,)
        )

        conn.commit()
