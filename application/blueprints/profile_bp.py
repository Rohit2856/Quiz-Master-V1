from flask import current_app, Blueprint, render_template, redirect, url_for, flash, send_from_directory
from flask_login import login_required, current_user
from application import db
from application.forms import ProfileForm
from application.models import User
from werkzeug.utils import secure_filename
from datetime import datetime, timezone
import os

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    # to check if uploaded file has an allowed extension
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@profile_bp.route('/')
@login_required
def profile():
    # Redirect to the current user profile
    return redirect(url_for('profile.view', username=current_user.username))

@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    # Edit user profile
    form = ProfileForm()

    if form.validate_on_submit():
        # Define upload_folder so it available for both remove and upload logic.
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'instance/uploads')
        os.makedirs(upload_folder, exist_ok=True)

        # Remove current avatar if checkbox is checked.
        if form.remove_avatar.data:
            if current_user.avatar:
                old_path = os.path.join(upload_folder, current_user.avatar)
                if os.path.exists(old_path):
                    os.remove(old_path)
            current_user.avatar = None
        
        # Handle new avatar upload.
        if form.avatar.data:
            file = form.avatar.data
            if file and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[-1].lower()
                filename = secure_filename(f"{current_user.id}_{datetime.now(timezone.utc).timestamp()}.{ext}")
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)
                current_user.avatar = filename

        # Update user fields from the form.
        current_user.full_name = form.full_name.data or current_user.full_name
        current_user.username = form.username.data or current_user.username
        current_user.email = form.email.data or current_user.email
        current_user.dob = form.dob.data if form.dob.data else current_user.dob
        current_user.bio = form.bio.data or current_user.bio
        current_user.location = form.location.data or current_user.location
        current_user.website = form.website.data or current_user.website
        current_user.qualification = form.qualification.data or current_user.qualification

        db.session.commit()

        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile.view', username=current_user.username))
    
    # Pre-fill the form fields with current user data for GET request or if form is invalid.
    form.full_name.data = current_user.full_name
    form.username.data = current_user.username
    form.email.data = current_user.email
    form.dob.data = current_user.dob
    form.bio.data = current_user.bio
    form.location.data = current_user.location
    form.website.data = current_user.website
    form.qualification.data = current_user.qualification

    return render_template('user/profile_edit.html', form=form)

@profile_bp.route('/uploads/<filename>')
@login_required
def serve_uploaded_file(filename):
    #Serve user-uploaded files stored in instance/uploads
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'instance/uploads')
    return send_from_directory(upload_folder, filename)

@profile_bp.route('/<username>')
@login_required
def view(username):
    # View user profile
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user/profile_view.html', 
                           user=user,
                           is_own_profile=(user.id == current_user.id))
