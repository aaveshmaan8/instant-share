import os
from pathlib import Path

# ================= BASE DIRECTORY =================
BASE_DIR = Path(__file__).resolve().parent

# ================= FOLDERS =================
UPLOAD_FOLDER = BASE_DIR / "uploads"
STATIC_FOLDER = BASE_DIR / "static"
DATABASE_PATH = BASE_DIR / "database.db"

# Ensure required folders exist
UPLOAD_FOLDER.mkdir(exist_ok=True)
STATIC_FOLDER.mkdir(exist_ok=True)

# ================= FILE SETTINGS =================
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
EXPIRY_TIME = 300  # 5 minutes
MAX_DOWNLOADS = 1  # one-time download

# ================= ENVIRONMENT =================
ENV = os.environ.get("FLASK_ENV", "production")
DEBUG = ENV == "development"

# ================= SECURITY =================
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

if not SECRET_KEY:
    # Fail fast in production
    if ENV == "production":
        raise RuntimeError("SECRET_KEY environment variable not set!")
    SECRET_KEY = "dev-secret-key"
