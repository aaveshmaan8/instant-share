import os

UPLOAD_FOLDER = "uploads"
STATIC_FOLDER = "static"
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
EXPIRY_TIME = 300  # 5 minutes

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)
