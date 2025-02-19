from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
from application.models import Admin
# Initialize SQLAlchemy
db = SQLAlchemy()

def initialize_default_admin():
    # Check if admin exists
    admin = Admin.query.filter_by(username='admin').first()
    if not admin:
        # Create admin with hashed password
        new_admin = Admin(
            username='admin',
            password=generate_password_hash('admin123')
        )
        db.session.add(new_admin)
        db.session.commit()
