import os
from datetime import timedelta
from pathlib import Path

# Base directory and paths
basedir = Path(__file__).resolve().parent
instance_path = basedir / 'instance'
upload_path = instance_path / 'uploads'

class Config:
    # Core Settings
    SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(24))
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f'sqlite:///{instance_path}/quiz_master.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security Headers
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)
    
    # File Uploads
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB
    UPLOAD_FOLDER = upload_path
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Flask-Login
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    REMEMBER_COOKIE_SECURE = True
    
    # Database Pooling (Production Only)
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "pool_size": 20,
        "max_overflow": 30
    }

class ProductionConfig(Config):
    # Production Security Enhancements
    SESSION_COOKIE_NAME = '__Secure-session'
    REMEMBER_COOKIE_NAME = '__Secure-remember_token'
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    # Development Settings
    DEBUG = True
    TESTING = True
    SQLALCHEMY_ECHO = True  # Show SQL queries
    SESSION_COOKIE_SECURE = False  # Allow HTTP
