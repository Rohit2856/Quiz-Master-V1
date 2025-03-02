from werkzeug.security import generate_password_hash
from application.extensions import db  # Import db from extensions
from flask import current_app

def initialize_default_admin():
    from application.models import Admin
    with current_app.app_context():  
        admin = Admin.query.filter_by(username='admin').first()
        if not admin:
            admin = Admin(username='admin', password=generate_password_hash('admin123'))
            db.session.add(admin)
            db.session.commit()