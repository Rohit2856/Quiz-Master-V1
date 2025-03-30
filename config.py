import os
from datetime import timedelta
from pathlib import Path
import pytz

# Define the IST timezone globally
IST = pytz.timezone('Asia/Kolkata')
# Base directory and paths
basedir = Path(__file__).resolve().parent
instance_path = basedir / 'instance'
upload_path = instance_path / 'uploads'
WTF_CSRF_ENABLED = False

class Config:
    # Core Settings
    # Use a FIXED SECRET_KEY instead of os.urandom(24)
    # (In production, set SECRET_KEY via environment variable or secrets manager)
    SECRET_KEY = os.environ.get('SECRET_KEY', '3bf124ce12af99d621833cd7f4bcf3cc1f64a5337eb77a5fb0dc70aa2d5eb93f')

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
    
    


class DevelopmentConfig(Config):
    # Development Settings
    DEBUG = False
    TESTING = True
    SQLALCHEMY_ECHO = True  # Show SQL queries
    

