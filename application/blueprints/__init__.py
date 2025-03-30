# Import and expose all blueprints in __init__.py to avoid circular imports 
from .profile_bp import profile_bp
from .stats_bp import stats_bp
from .main_bp import main_bp
from .api_bp import api_bp
from .auth_bp import auth_bp
from .admin_bp import admin_bp
from .user_bp import user_bp

# Listed for easier registration in application factory 
all_blueprints = [api_bp, auth_bp, admin_bp, user_bp, main_bp, profile_bp, stats_bp]
