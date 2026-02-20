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
    MAX_DOWNLOADS,
    DATABASE_URL
)

from database import get_connection

TABLE_NAME = "files"


# ================= HELPER =================
def is_postgres():
    return bool(DATABASE_URL)


def placeholder():
    return "%s" if is_postgres() else "?"


# ================= LOG IP ACTION =================
def log_ip_action(code, action, ip):
    ph = placeholder()
    current_time = int(time.time())

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            INSERT INTO ip_logs
            (code, action, ip_address, action_time)
            VALUES ({ph}, {ph}, {ph}, {ph})
        """, (code, action, ip, current_time))
        conn.commit()


# ================= GENERATE UNIQUE CODE =================
def generate_code(length=6):
    characters = string.ascii_uppercase + string.digits
    ph = placeholder()

    while True:
        code = ''.join(secrets.choice(characters) for _ in range(length))

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT 1 FROM {TABLE_NAME} WHERE code = {ph}",
                (code,)
            )
            exists = cursor.fetchone()

        if not exists:
            return code


# ================= CLEANUP EXPIRED FILES =================
def cleanup_expired_files():
    current_time = int(time.time())
    ph = placeholder()

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT code FROM {TABLE_NAME} WHERE expires_at < {ph}",
            (current_time,)
        )
        expired = cursor.fetchall()

    for row in expired:
        code = row["code"] if not is_postgres() else row[0]
        delete_file(code)


# ================= SAVE FILES =================
def save_files(files, uploader_ip):

    cleanup_expired_files()

    if not files:
        return None, "No files uploaded."

    code = generate_code()
    folder_path = os.path.join(UPLOAD_FOLDER, code)
    os.makedirs(folder_path, exist_ok=True)

    upload_time = int(time.time())
    expires_at = upload_time + EXPIRY_TIME
    created_date = time.strftime("%Y-%m-%d")

    total_size = 0
    ph = placeholder()

    try:
        for file in files:
            file.seek(0, os.SEEK_END)
            size = file.tell()
            file.seek(0)

            if size > MAX_FILE_SIZE:
                return None, "One file exceeds max size."

            filename = secure_filename(file.filename)
            if not filename:
                return None, "Invalid filename."

            file.save(os.path.join(folder_path, filename))
            total_size += size

        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                INSERT INTO {TABLE_NAME}
                (code, filename, original_name, upload_time, expires_at,
                 downloads, created_date, uploader_ip, downloader_ip, file_size)
                VALUES ({ph}, {ph}, {ph}, {ph}, {ph},
                        0, {ph}, {ph}, NULL, {ph})
            """, (
                code,
                code,
                "multiple_files",
                upload_time,
                expires_at,
                created_date,
                uploader_ip,
                total_size
            ))
            conn.commit()

        generate_qr(code)

        # 🔥 LOG UPLOAD IP
        log_ip_action(code, "UPLOAD", uploader_ip)

    except Exception as e:
        print("UPLOAD ERROR:", e)
        delete_file(code)
        return None, str(e)

    return code, None

# ================= GENERATE QR =================
def generate_qr(code):
    try:
        full_url = f"/download_direct/{code}"
        qr = qrcode.make(full_url)

        os.makedirs(STATIC_FOLDER, exist_ok=True)
        qr_path = os.path.join(STATIC_FOLDER, f"{code}.png")
        qr.save(qr_path)

    except Exception as e:
        print("QR ERROR:", e)


# ================= PROCESS DOWNLOAD =================
def process_download(code, downloader_ip):

    cleanup_expired_files()
    ph = placeholder()

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * FROM {TABLE_NAME} WHERE code = {ph}",
            (code,)
        )
        file_info = cursor.fetchone()

        if not file_info:
            return None, "Invalid or expired code!"

        downloads = (
            file_info["downloads"]
            if not is_postgres()
            else file_info[6]
        )

        if downloads >= MAX_DOWNLOADS:
            delete_file(code)
            return None, "Download limit reached!"

        folder_path = os.path.join(UPLOAD_FOLDER, code)

        if not os.path.exists(folder_path):
            return None, "Files not found!"

        cursor.execute(f"""
            UPDATE {TABLE_NAME}
            SET downloads = downloads + 1,
                downloader_ip = {ph}
            WHERE code = {ph}
        """, (downloader_ip, code))
        conn.commit()

        # 🔥 LOG DOWNLOAD IP
        log_ip_action(code, "DOWNLOAD", downloader_ip)

    files = os.listdir(folder_path)

    # SINGLE FILE
    if len(files) == 1:
        file_path = os.path.join(folder_path, files[0])
        response = send_file(
            file_path,
            as_attachment=True,
            download_name=files[0]
        )

        if downloads + 1 >= MAX_DOWNLOADS:
            delete_files_only(code)

        return response, None

    # MULTIPLE FILES → ZIP
    zip_path = os.path.join(UPLOAD_FOLDER, f"{code}.zip")

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for filename in files:
            zipf.write(
                os.path.join(folder_path, filename),
                arcname=filename
            )

    response = send_file(
        zip_path,
        as_attachment=True,
        download_name=f"{code}.zip"
    )

    if downloads + 1 >= MAX_DOWNLOADS:
        delete_files_only(code)

    return response, None


# ================= DELETE FILES ONLY =================
def delete_files_only(code):

    folder_path = os.path.join(UPLOAD_FOLDER, code)
    zip_path = os.path.join(UPLOAD_FOLDER, f"{code}.zip")
    qr_path = os.path.join(STATIC_FOLDER, f"{code}.png")

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

    if os.path.exists(zip_path):
        try:
            os.remove(zip_path)
        except:
            pass

    if os.path.exists(qr_path):
        try:
            os.remove(qr_path)
        except:
            pass


# ================= DELETE FULL RECORD =================
def delete_file(code):

    ph = placeholder()

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            f"DELETE FROM {TABLE_NAME} WHERE code = {ph}",
            (code,)
        )
        conn.commit()

    delete_files_only(code)