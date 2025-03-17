from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from application.forms import UserRegistrationForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, DateField, SubmitField, validators
from wtforms.fields import DateField
from flask_login import login_user, logout_user, login_required, current_user
from application.models import User
from application import db
from sqlalchemy.exc import IntegrityError
from wtforms.validators import InputRequired, Length, EqualTo
import uuid , os, email_validator

auth_bp = Blueprint('auth', __name__)
# -------------------------
# Form Definitions
# -------------------------
class LoginForm(FlaskForm):
    username = StringField('Username', [
        InputRequired(),
        Length(min=4, max=25)
    ])
    password = PasswordField('Password', [
        InputRequired(),
        Length(min=8)
    ])
    remember = BooleanField('Remember Me')  # Added missing field
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', [
        InputRequired(),
        Length(min=4, max=25)
    ])
    password = PasswordField('Password', [
        InputRequired(),
        Length(min=8),
        EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    full_name = StringField('Full Name', [
        InputRequired(),
        Length(min=2, max=50)
    ])
    qualification = StringField('Qualification')
    dob = DateField('Date of Birth', format='%Y-%m-%d')
    avatar = FileField('Profile Picture', validators=[
        FileAllowed(['jpg', 'png', 'gif'], 'Images only!')
    ])
    submit = SubmitField('Register')

# -------------------------
# Authentication Routes
# -------------------------
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = UserRegistrationForm()
    if form.validate_on_submit():
        try:
            filename = None
            if form.avatar.data:
                filename = secure_filename(f"{uuid.uuid4().hex}_{form.avatar.data.filename}")
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                form.avatar.data.save(file_path)

            new_user = User(
                username=form.username.data,
                email=form.email.data,
                password_hash=generate_password_hash(form.password.data),
                full_name=form.full_name.data,
                qualification=form.qualification.data,
                dob=form.dob.data,
                avatar=filename
            )

            db.session.add(new_user)
            db.session.commit()
            
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.user_login'))

        except IntegrityError:  # Catch duplicate username/email errors
            db.session.rollback()
            existing_user = User.query.filter(
                (User.username == form.username.data) | (User.email == form.email.data)
            ).first()
            
            if existing_user:
                flash("User with this username or email already exists.", "danger")
            else:
                flash("An unexpected database error occurred. Please try again.", "danger")

        except Exception as e:
            db.session.rollback()
            flash('Registration failed due to a server error. Please try again.', 'danger')

    return render_template('auth/register.html', form=form)


@auth_bp.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if current_user.is_authenticated:
        return redirect(url_for('user.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user, remember=form.remember.data)  
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('user.dashboard'))
        
        flash('Invalid username or password', 'danger')  
        print("Login failed: Invalid credentials")  

    return render_template('auth/user_login.html', form=form)


@auth_bp.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        else:
            flash("You don't have admin privileges.", "danger")
            return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.is_admin and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin.dashboard'))
        else:
            flash('Invalid admin credentials.', 'danger')
            return redirect(url_for('auth.admin_login'))

    return render_template('auth/admin_login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('auth.user_login'))

# -------------------------
# Helper Functions
# -------------------------
def allowed_file(filename):
    """Validate uploaded file extensions"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
