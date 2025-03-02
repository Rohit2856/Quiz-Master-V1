# application/decorators.py
from functools import wraps
from flask import abort, redirect, url_for
from flask_login import current_user

def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        # Check if user is authenticated and is admin
        if not current_user.is_authenticated:
            return redirect(url_for('user_login'))
        
        # Assuming you have an `is_admin` boolean in User model
        if not current_user.is_admin:
            abort(403)  # Forbidden
        return func(*args, **kwargs)
    return decorated_view
