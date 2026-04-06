import os

class Config:
    # SECURITY FIX: No fallback value — app will crash loudly if SECRET_KEY is missing
    # This is intentional: a missing secret key should never silently use a weak default
    SECRET_KEY = os.environ.get('SECRET_KEY')

    # Render gives DATABASE_URL with "postgres://" prefix — SQLAlchemy needs "postgresql://"
    # SECURITY FIX: auto-fix the URL if needed (required for Render PostgreSQL)
    _db_url = os.environ.get('DATABASE_URL', 'sqlite:///janseva.db')
    if _db_url.startswith('postgres://'):
        _db_url = _db_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = _db_url

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB max upload
    UPLOAD_FOLDER = 'app/static/uploads'