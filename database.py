import os
import psycopg2
import psycopg2.extras

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS instantshare_files (
            id SERIAL PRIMARY KEY,
            code VARCHAR(10) UNIQUE NOT NULL,
            filename TEXT,
            original_name TEXT,
            upload_time BIGINT,
            expires_at BIGINT,
            downloads INTEGER DEFAULT 0,
            upload_ip TEXT,
            last_download_ip TEXT,
            file_size BIGINT DEFAULT 0
        );
    """)

    conn.commit()
    conn.close()
