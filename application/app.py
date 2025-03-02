from flask import Flask
from flask_login import LoginManager
from application.extensions import db  
from application.database import initialize_default_admin

#initialize the app and login_manager
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
        # Import models after db initialization
        from application.models import User, Admin, Subject, Chapter, Quiz, Question, Score
        db.create_all()
        initialize_default_admin()

    # Import routes after app context setup
    with app.app_context():
        from application import routes

    # User loader
    @login_manager.user_loader
    def load_user(user_id):
        admin = Admin.query.get(user_id)
        return admin or User.query.get(int(user_id))

    return app
