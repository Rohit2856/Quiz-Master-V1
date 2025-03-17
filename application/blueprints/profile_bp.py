from flask import current_app, Blueprint, render_template, request, redirect, url_for, flash, send_from_directory
from flask_login import login_required, current_user, login_user
from application import db
from application.forms import ProfileForm
from application.models import User
from werkzeug.utils import secure_filename
from datetime import datetime, timezone
import os

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

# -------------------------
# Profile Management
# -------------------------

@profile_bp.route('/')
@login_required
def profile():
    """Redirect to the current user's profile"""
    return redirect(url_for('profile.view', username=current_user.username))
  

@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    form = ProfileForm()

    if form.validate_on_submit():
        if form.avatar.data:
            file = form.avatar.data
            if file and allowed_file(file.filename):
                upload_folder = current_app.config.get('UPLOAD_FOLDER', 'instance/uploads')
                os.makedirs(upload_folder, exist_ok=True)

                ext = file.filename.rsplit('.', 1)[-1].lower()
                filename = secure_filename(f"{current_user.id}_{datetime.now(timezone.utc).timestamp()}.{ext}")
                file_path = os.path.join(upload_folder, filename)

                file.save(file_path)
                current_user.avatar = filename

        # 🔹 Update profile fields
        current_user.bio = form.bio.data or current_user.bio
        current_user.location = form.location.data or current_user.location
        current_user.website = form.website.data or current_user.website

        db.session.commit()

        # Force refresh the user session to get updated data
        login_user(current_user, force=True)

        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile.view', username=current_user.username))

    # Pre-fill the form with existing user data
    form.bio.data = current_user.bio
    form.location.data = current_user.location
    form.website.data = current_user.website

    return render_template('user/profile_edit.html', form=form)

@profile_bp.route('/uploads/<filename>')
@login_required
def serve_uploaded_file(filename):
    """Serve user-uploaded files stored in instance/uploads"""
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'instance/uploads')
    return send_from_directory(upload_folder, filename)


@profile_bp.route('/<username>')
@login_required
def view(username):
    """View user profile"""
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user/profile_view.html', 
                           user=user,
                           is_own_profile=(user.id == current_user.id))

# -------------------------
# Helper Functions
# -------------------------

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Check if uploaded file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
