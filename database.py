import os
import sqlite3
import psycopg2
import psycopg2.extras

from config import DATABASE_PATH


# ================= GET CONNECTION =================
def get_connection():

    database_url = os.environ.get("DATABASE_URL")

    # ===== PostgreSQL (Render) =====
    if database_url:

        # Fix old postgres:// issue
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)

        try:
            conn = psycopg2.connect(
                database_url,
                sslmode="require",
                connect_timeout=5   # 🔥 prevents hanging
            )
            return conn

        except Exception as e:
            print("❌ DB CONNECTION ERROR:", e)
            raise e

    # ===== SQLite (Local) =====
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ================= INITIALIZE DATABASE =================
def init_db():

    try:
        conn = get_connection()
        cursor = conn.cursor()

        database_url = os.environ.get("DATABASE_URL")

        # ===== PostgreSQL =====
        if database_url:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id SERIAL PRIMARY KEY,
                    code VARCHAR(10) UNIQUE NOT NULL,
                    filename TEXT NOT NULL,
                    original_name TEXT NOT NULL,
                    upload_time BIGINT NOT NULL,
                    expires_at BIGINT NOT NULL,
                    downloads INTEGER DEFAULT 0,
                    created_date TEXT,
                    uploader_ip TEXT,
                    downloader_ip TEXT,
                    file_size BIGINT DEFAULT 0
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ip_logs (
                    id SERIAL PRIMARY KEY,
                    code VARCHAR(10),
                    action VARCHAR(20),
                    ip_address TEXT,
                    action_time BIGINT
                );
            """)

        # ===== SQLite =====
        else:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT UNIQUE NOT NULL,
                    filename TEXT NOT NULL,
                    original_name TEXT NOT NULL,
                    upload_time INTEGER NOT NULL,
                    expires_at INTEGER NOT NULL,
                    downloads INTEGER DEFAULT 0,
                    created_date TEXT,
                    uploader_ip TEXT,
                    downloader_ip TEXT,
                    file_size INTEGER DEFAULT 0
                );
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ip_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT,
                    action TEXT,
                    ip_address TEXT,
                    action_time INTEGER
                );
            """)

        conn.commit()
        conn.close()

        print("✅ Database initialized successfully")

    except Exception as e:
        print("❌ DB INIT ERROR:", e)