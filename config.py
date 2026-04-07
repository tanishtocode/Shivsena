import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, "instance")

# Ensure instance folder exists
os.makedirs(INSTANCE_DIR, exist_ok=True)


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY")

    database_url = os.environ.get("DATABASE_URL")

    # Fix old postgres:// style if ever used on Render
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    # If using local sqlite, force absolute safe path
    if not database_url or database_url.startswith("sqlite:///"):
        database_url = f"sqlite:///{os.path.join(INSTANCE_DIR, 'janseva.db')}"

    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
    FLASK_ENV = os.environ.get("FLASK_ENV", "development")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

    UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "static", "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}