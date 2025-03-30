from flask import Flask
from config import Config
from .extensions import db, migrate, login_manager
from flask_login import current_user
from flask_migrate import Migrate

migrate = Migrate()

def get_attribute(obj, attr):
    return getattr(obj, attr, None)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with app context
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    login_manager.login_view = "auth.user_login"
    login_manager.login_message_category = "warning"

    app.jinja_env.filters['get_attribute'] = get_attribute

    # Register blueprints
    register_blueprints(app)

    @app.cli.command("init-db")
    def init_db():
        # Initialize the database and create default admin.
        from application.models import User, db

        db.create_all()

        # Check if admin user exists
        admin_user = User.query.filter_by(is_admin=True).first()
        if not admin_user:
            admin = User(
                username="admin",
                email="admin@example.com", 
                full_name="System Admin",
                is_admin=True,
                is_active=True
            )
            admin.set_password("admin123")  # Set a default password securely
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully.")

        print("Database initialized successfully.")

    @app.context_processor
    def inject_user():
        return dict(current_user=current_user)
    print("Jinja loader search paths:", app.jinja_loader.searchpath)
    return app

def register_blueprints(app):
    from application.blueprints.admin_bp import admin_bp
    from application.blueprints.auth_bp import auth_bp
    from application.blueprints.user_bp import user_bp
    from application.blueprints.main_bp import main_bp
    from application.blueprints.api_bp import api_bp
    from application.blueprints.profile_bp import profile_bp
    from application.blueprints.stats_bp import stats_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(profile_bp, url_prefix="/profile")
    app.register_blueprint(stats_bp, url_prefix="/stats")

@login_manager.user_loader
def load_user(user_id):
    from application.models import User
    return User.query.get(int(user_id))

