from functools import wraps
from flask import abort, redirect, url_for
from flask_login import current_user

def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        # Check authentication first 
        if not current_user.is_authenticated:
            return redirect(url_for('auth.user_login')) # Redirect to login page if not authenticated 
        
        # Check admin status (single User model approach) 
        if not getattr(current_user, 'is_admin', False):
            abort(403)  # Forbidden 
            
        return func(*args, **kwargs)
    return decorated_view
