from flask import Flask
from flask_login import LoginManager
from application.database import db, initialize_default_admin

# Initialize Flask app and LoginManager
app = None
login_manager = LoginManager()

def create_app():
    global app
    app = Flask(__name__)
    app.debug = True

    # Configuration
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_master.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Create tables and default admin
    with app.app_context():
        from application.models import User, Admin, Subject, Chapter, Quiz, Question, Score
        db.create_all()  # Create tables 
        initialize_default_admin()  # to define admin user

    # Import routes
    with app.app_context():
        from application import routes

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        # Check if user is admin
        admin = Admin.query.get(user_id)
        if admin:
            return admin
        # Otherwise, return regular user
        return User.query.get(int(user_id))

    return app  # Return the Flask app instance
