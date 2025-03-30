from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, DateField, SubmitField
from wtforms.validators import InputRequired, Length, EqualTo, Email
from flask_login import login_user, logout_user, login_required, current_user
from application.models import User
from application import db
from sqlalchemy.exc import IntegrityError
import uuid, os

# Blueprint Definition
auth_bp = Blueprint('auth', __name__)

# -------------------------
# Form Definitions
# -------------------------
class LoginForm(FlaskForm):
    username = StringField('Username', [InputRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', [InputRequired(), Length(min=8)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', [InputRequired(), Length(min=4, max=25)])
    email = StringField('Email', [InputRequired(), Email()])  # Added email field
    password = PasswordField('Password', [InputRequired(), Length(min=8), EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm Password')
    full_name = StringField('Full Name', [InputRequired(), Length(min=2, max=50)])
    qualification = StringField('Qualification')
    dob = DateField('Date of Birth', format='%Y-%m-%d')
    avatar = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'png', 'gif'], 'Images only!')])
    submit = SubmitField('Register')

# -------------------------
# Authentication Routes
# -------------------------
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
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
        
        except IntegrityError:
            db.session.rollback()
            flash("User with this username or email already exists.", "danger")
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
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Login successful!', 'success')
            return redirect(request.args.get('next') or url_for('user.dashboard'))
        
        flash('Invalid username or password', 'danger')
    
    return render_template('auth/user_login.html', form=form)

@auth_bp.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        flash("You don't have admin privileges.", "danger")
        return redirect(url_for('main.index'))
    
    if form.validate_on_submit():
        admin_user = User.get_admin()
        if admin_user and admin_user.username == form.username.data and check_password_hash(admin_user.password_hash, form.password.data):
            login_user(admin_user)
            return redirect(url_for('admin.dashboard'))
        
        flash('Invalid admin credentials.', 'danger')
    
    return render_template('auth/admin_login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('auth.user_login'))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
