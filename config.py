import os
from pathlib import Path

# ================= BASE DIRECTORY =================
BASE_DIR = Path(__file__).resolve().parent

# ================= FOLDERS =================
UPLOAD_FOLDER = BASE_DIR / "uploads"
STATIC_FOLDER = BASE_DIR / "static"
DATABASE_PATH = BASE_DIR / "database.db"

# Ensure required folders exist
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
STATIC_FOLDER.mkdir(parents=True, exist_ok=True)

# ================= FILE SETTINGS =================
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
EXPIRY_TIME = 300  # 5 minutes
MAX_DOWNLOADS = 1  # one-time download

# ================= ENVIRONMENT =================
ENV = os.environ.get("FLASK_ENV", "production")
DEBUG = ENV == "development"

# ================= SECURITY =================
SECRET_KEY = os.environ.get("SECRET_KEY")

if not SECRET_KEY:
    # If running locally, auto-generate dev key
    SECRET_KEY = "dev-secret-key"


# ================= ADMIN CONFIG =================
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")


DATABASE_URL = os.getenv("DATABASE_URL")

