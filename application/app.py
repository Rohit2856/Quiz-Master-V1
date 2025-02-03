from flask import Flask
from flask_login import LoginManager
from application.database import db

# Initialize Flask app and LoginManager
app = None
login_manager = LoginManager()

def create_app():
    global app
    app = Flask(__name__)
    app.debug = True

    # Application configuration
    app.config['SECRET_KEY'] = 'your_secret_key_here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_master.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Import routes
    with app.app_context():
        from application import routes  # Import routes here to avoid circular imports
        return app
