import os
import time
import secrets
import string
import qrcode
from flask import send_file
from werkzeug.utils import secure_filename
from config import (
    UPLOAD_FOLDER,
    STATIC_FOLDER,
    MAX_FILE_SIZE,
    EXPIRY_TIME,
    MAX_DOWNLOADS
)
from database import get_connection


# ================= GENERATE UNIQUE CODE =================
def generate_code(length=6):
    characters = string.ascii_uppercase + string.digits

    while True:
        code = ''.join(secrets.choice(characters) for _ in range(length))

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM files WHERE code = ?", (code,))
            exists = cursor.fetchone()

        if not exists:
            return code


# ================= CLEANUP EXPIRED FILES =================
def cleanup_expired_files():
    current_time = int(time.time())

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT code, filename FROM files WHERE expires_at < ?",
            (current_time,)
        )
        expired = cursor.fetchall()

        for row in expired:
            filepath = os.path.join(UPLOAD_FOLDER, row["filename"])
            qr_path = os.path.join(STATIC_FOLDER, f"{row['code']}.png")

            if os.path.exists(filepath):
                os.remove(filepath)

            if os.path.exists(qr_path):
                os.remove(qr_path)

        cursor.execute(
            "DELETE FROM files WHERE expires_at < ?",
            (current_time,)
        )

        conn.commit()


# ================= SAVE FILE =================
def save_file(file):

    cleanup_expired_files()

    # Check file size
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)

    if size > MAX_FILE_SIZE:
        return None, f"File too large! Max {MAX_FILE_SIZE // (1024*1024)}MB allowed."

    code = generate_code()
    original_name = secure_filename(file.filename)
    filename = f"{code}_{original_name}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    try:
        file.save(filepath)
    except Exception:
        return None, "Failed to save file."

    upload_time = int(time.time())
    expires_at = upload_time + EXPIRY_TIME

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO files
                (code, filename, original_name, upload_time, expires_at, downloads)
                VALUES (?, ?, ?, ?, ?, 0)
            """, (code, filename, original_name, upload_time, expires_at))

            conn.commit()
    except Exception:
        if os.path.exists(filepath):
            os.remove(filepath)
        return None, "Database error."

    return code, None


# ================= GENERATE QR =================
def generate_qr(download_url, code):
    try:
        qr = qrcode.make(download_url)
        qr_path = os.path.join(STATIC_FOLDER, f"{code}.png")
        qr.save(qr_path)
    except Exception:
        pass  # QR failure should not crash upload


# ================= PROCESS DOWNLOAD =================
def process_download(code):

    cleanup_expired_files()

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM files WHERE code = ?", (code,))
        file_info = cursor.fetchone()

        if not file_info:
            return None, "Invalid or expired code!"

        current_time = int(time.time())

        if current_time > file_info["expires_at"]:
            delete_file(code)
            return None, "File expired!"

        if file_info["downloads"] >= MAX_DOWNLOADS:
            delete_file(code)
            return None, "Download limit reached!"

        filepath = os.path.join(UPLOAD_FOLDER, file_info["filename"])

        if not os.path.exists(filepath):
            delete_file(code)
            return None, "File not found!"

        # Increase download count
        cursor.execute(
            "UPDATE files SET downloads = downloads + 1 WHERE code = ?",
            (code,)
        )
        conn.commit()

    response = send_file(
        filepath,
        as_attachment=True,
        download_name=file_info["original_name"]
    )

    # If one-time download → delete immediately
    if MAX_DOWNLOADS == 1:
        delete_file(code)

    return response, None


# ================= DELETE FILE =================
def delete_file(code):

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT filename FROM files WHERE code = ?", (code,))
        file_info = cursor.fetchone()

        if not file_info:
            return

        filepath = os.path.join(UPLOAD_FOLDER, file_info["filename"])
        qr_path = os.path.join(STATIC_FOLDER, f"{code}.png")

        try:
            if os.path.exists(filepath):
                os.remove(filepath)

            if os.path.exists(qr_path):
                os.remove(qr_path)

            cursor.execute("DELETE FROM files WHERE code = ?", (code,))
            conn.commit()

        except Exception:
            pass
