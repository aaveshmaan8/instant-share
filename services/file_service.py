import os
import time
import secrets
import string
import zipfile
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
            "SELECT DISTINCT code FROM files WHERE expires_at < ?",
            (current_time,)
        )
        expired_codes = cursor.fetchall()

    for row in expired_codes:
        delete_file(row["code"])


# ================= SAVE MULTIPLE FILES (ONE CODE) =================
def save_files(files):

    cleanup_expired_files()

    if not files:
        return None, "No files uploaded."

    code = generate_code()
    folder_path = os.path.join(UPLOAD_FOLDER, code)
    os.makedirs(folder_path, exist_ok=True)

    upload_time = int(time.time())
    expires_at = upload_time + EXPIRY_TIME

    try:
        for file in files:

            # File size check
            file.seek(0, os.SEEK_END)
            size = file.tell()
            file.seek(0)

            if size > MAX_FILE_SIZE:
                return None, "One of the files exceeds max size."

            filename = secure_filename(file.filename)

            if not filename:
                return None, "Invalid filename."

            file.save(os.path.join(folder_path, filename))

        # Save ONE record in database
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO files
                (code, filename, original_name, upload_time, expires_at, downloads)
                VALUES (?, ?, ?, ?, ?, 0)
            """, (code, code, "multiple_files", upload_time, expires_at))
            conn.commit()

        # Generate QR
        download_url = f"/download_direct/{code}"
        generate_qr(download_url, code)

    except Exception as e:
        delete_file(code)
        return None, "Upload failed."

    return code, None


# ================= GENERATE QR =================
def generate_qr(download_url, code):
    try:
        full_url = f"http://127.0.0.1:5000{download_url}"
        qr = qrcode.make(full_url)

        os.makedirs(STATIC_FOLDER, exist_ok=True)
        qr_path = os.path.join(STATIC_FOLDER, f"{code}.png")
        qr.save(qr_path)

    except Exception:
        pass


# ================= PROCESS DOWNLOAD =================
def process_download(code):

    cleanup_expired_files()

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM files WHERE code = ?", (code,))
        file_info = cursor.fetchone()

        if not file_info:
            return None, "Invalid or expired code."

        current_time = int(time.time())

        if current_time > file_info["expires_at"]:
            delete_file(code)
            return None, "File expired."

        if file_info["downloads"] >= MAX_DOWNLOADS:
            delete_file(code)
            return None, "Download limit reached."

        folder_path = os.path.join(UPLOAD_FOLDER, code)

        if not os.path.exists(folder_path):
            delete_file(code)
            return None, "Files not found."

        # Increase download count
        cursor.execute(
            "UPDATE files SET downloads = downloads + 1 WHERE code = ?",
            (code,)
        )
        conn.commit()

    # Create ZIP
    zip_path = os.path.join(UPLOAD_FOLDER, f"{code}.zip")

    try:
        if os.path.exists(zip_path):
            os.remove(zip_path)

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename in os.listdir(folder_path):
                zipf.write(
                    os.path.join(folder_path, filename),
                    arcname=filename
                )

    except Exception:
        return None, "Failed to create ZIP."

    response = send_file(
        zip_path,
        as_attachment=True,
        download_name=f"{code}.zip"
    )

    # Auto delete if single download allowed
    if MAX_DOWNLOADS == 1:
        delete_file(code)

    return response, None


# ================= DELETE FILE =================
def delete_file(code):

    folder_path = os.path.join(UPLOAD_FOLDER, code)
    zip_path = os.path.join(UPLOAD_FOLDER, f"{code}.zip")
    qr_path = os.path.join(STATIC_FOLDER, f"{code}.png")

    # Remove DB record
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM files WHERE code = ?", (code,))
        conn.commit()

    # Remove folder
    if os.path.exists(folder_path):
        for file in os.listdir(folder_path):
            try:
                os.remove(os.path.join(folder_path, file))
            except:
                pass
        try:
            os.rmdir(folder_path)
        except:
            pass

    # Remove ZIP
    if os.path.exists(zip_path):
        try:
            os.remove(zip_path)
        except:
            pass

    # Remove QR
    if os.path.exists(qr_path):
        try:
            os.remove(qr_path)
        except:
            pass
