from flask import Flask
from config import Config
from .extensions import db, migrate, login_manager
from flask_login import current_user

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with app context
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    login_manager.login_view = "auth.user_login"
    login_manager.login_message_category = "warning"

    # Register blueprints
    register_blueprints(app)

    # CLI command to initialize DB explicitly 
    @app.cli.command("init-db")
    def init_db():
        """Initialize DB tables and create default admin."""
        from application.models import User
        db.create_all()

        if not User.query.filter_by(is_admin=True).first():
            admin = User(
                username="admin",
                full_name="Administrator",
                is_admin=True,
            )
            admin.password = "admin123"
            db.session.add(admin)
            db.session.commit()
            print("Default admin account created.")

        print("Database initialized successfully.")

    @app.context_processor
    def inject_user():
        return dict(current_user=current_user)

    return app

def register_blueprints(app):
    from application.blueprints.admin_bp import admin_bp
    from application.blueprints.auth_bp import auth_bp
    from application.blueprints.user_bp import user_bp
    from application.blueprints.main_bp import main_bp
    from application.blueprints.reports_bp import reports_bp
    from application.blueprints.api_bp import api_bp
    from application.blueprints.profile_bp import profile_bp
    from application.blueprints.stats_bp import stats_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(reports_bp, url_prefix="/reports")
    app.register_blueprint(api_bp, url_prefix="/api")
    app.register_blueprint(profile_bp, url_prefix="/profile")
    app.register_blueprint(stats_bp, url_prefix="/stats")

@login_manager.user_loader
def load_user(user_id):
    from application.models import User
    return User.query.get(int(user_id))
