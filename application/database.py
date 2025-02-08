from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
# Initialize SQLAlchemy
db = SQLAlchemy()
def initialize_default_admin():
    from application.models import Admin

    # Create default admin if not exists
    default_admin = Admin.query.filter_by(username='admin').first()
    if not default_admin:
        admin = Admin(
            username='admin',
            password=generate_password_hash('admin123')  # Hashed password
        )
        db.session.add(admin)
        db.session.commit()
