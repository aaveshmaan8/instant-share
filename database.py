import os
import sqlite3
import psycopg2
import psycopg2.extras
from config import DATABASE_PATH

# Detect Render PostgreSQL
DATABASE_URL = os.environ.get("DATABASE_URL")


# ================= GET CONNECTION =================
def get_connection():

    # ================= POSTGRESQL (Render) =================
    if DATABASE_URL:
        conn = psycopg2.connect(DATABASE_URL)
        return conn

    # ================= SQLITE (Local) =================
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ================= INITIALIZE DATABASE =================
def init_db():

    conn = get_connection()
    cursor = conn.cursor()

    # ================= POSTGRESQL TABLE =================
    if DATABASE_URL:
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

    # ================= SQLITE TABLE =================
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

    conn.commit()
    conn.close()
