from flask import current_app as app
from flask import (render_template, request, redirect, url_for, flash, session, abort)
from flask_login import login_user, login_required, logout_user, current_user
from .database import db
from application.models import User, Admin 
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/initialize_db')
def initialize_db():
    """
    Route to initialize the database schema.
    
    This will create all tables defined in models.py.
    
    Warning: Running this route will drop all existing tables and recreate them.
             Use with caution in production environments.
    
    Returns:
        str: Success message after initializing the database.
    """
    
    # Drop all existing tables (if any) and recreate them
    with app.app_context():
        try:
            # Drop all tables (for development purposes only!)
            db.drop_all()
            
            # Create new tables based on models.py definitions
            db.create_all()
            
            return "Database initialized successfully!"
        except Exception as e:
            return f"An error occurred while initializing the database: {str(e)}"

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        qualification = request.form.get('qualification')
        dob = request.form.get('dob')

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))

        new_user = User(
            username=username,
            password=generate_password_hash(password),
            full_name=full_name,
            qualification=qualification,
            dob=dob
        )

        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('user_login'))

    return render_template('register.html')

@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            flash('Invalid credentials!', 'danger')
            return redirect(url_for('user_login'))

        login_user(user)
        return redirect(url_for('user_dashboard'))

    return render_template('user_login.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        admin = Admin.query.filter_by(username=username).first()
        if not admin or not check_password_hash(admin.password, password):
            flash('Invalid admin credentials!', 'danger')
            return redirect(url_for('admin_login'))

        login_user(admin)
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))

@app.route('/user_dashboard')
@login_required
def user_dashboard():
    return render_template('user_dashboard.html')

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    return render_template('admin_dashboard.html')
