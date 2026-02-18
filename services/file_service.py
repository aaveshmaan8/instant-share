import os
import random
import string
import time
import io
import qrcode
from flask import send_file
from werkzeug.utils import secure_filename
from config import UPLOAD_FOLDER, STATIC_FOLDER, MAX_FILE_SIZE, EXPIRY_TIME


file_storage = {}

def generate_code():
    characters = string.ascii_uppercase + string.digits

    while True:
        code = ''.join(random.choices(characters, k=6))
        if code not in file_storage:
            return code


def save_file(file):
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    file.seek(0)

    if file_length > MAX_FILE_SIZE:
        return None, f"File too large! Max {MAX_FILE_SIZE // (1024*1024)}MB allowed."

    code = generate_code()

    original_name = secure_filename(file.filename)
    filename = code + "_" + original_name
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    file.save(filepath)

    file_storage[code] = {
        "filename": filename,
        "original_name": original_name,
        "upload_time": time.time()
    }

    return code, None


def generate_qr(download_url, code):
    qr = qrcode.make(download_url)
    qr_path = os.path.join(STATIC_FOLDER, f"{code}.png")
    qr.save(qr_path)


def process_download(code):
    file_info = file_storage.get(code)

    if not file_info:
        return None, "Invalid or expired code!"

    if time.time() - file_info["upload_time"] > EXPIRY_TIME:
        delete_file(code)
        return None, "File expired!"

    filepath = os.path.join(UPLOAD_FOLDER, file_info["filename"])

    if not os.path.exists(filepath):
        delete_file(code)
        return None, "File not found!"

    with open(filepath, "rb") as f:
        file_data = f.read()

    delete_file(code)

    return send_file(
        io.BytesIO(file_data),
        as_attachment=True,
        download_name=file_info["original_name"]
    ), None


def delete_file(code):
    file_info = file_storage.get(code)

    if file_info:
        filepath = os.path.join(UPLOAD_FOLDER, file_info["filename"])
        qr_path = os.path.join(STATIC_FOLDER, f"{code}.png")

        if os.path.exists(filepath):
            os.remove(filepath)

        if os.path.exists(qr_path):
            os.remove(qr_path)

        file_storage.pop(code, None)
