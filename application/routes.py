from flask import (
    render_template, request, redirect, url_for, flash,
    session, abort, jsonify
)
from flask_login import login_user, login_required, logout_user, current_user
from datetime import datetime, timezone
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from application import app, db
from application.models import User, Admin, Subject, Chapter, Quiz, Question, Score
from application.decorators import admin_required
import os

# -------------------------
# Database Initialization
# -------------------------
@app.route('/initialize_db')
def initialize_db():
    # DEVELOPMENT ROUTE - Drops and recreates all database tables
    with app.app_context():
        db.drop_all()
        db.create_all()
        initialize_default_admin()
    return "Database initialized!"

# -------------------------
# Authentication Routes
# -------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    # handle new user registration with form validation
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        qualification = request.form.get('qualification')
        dob = request.form.get('dob')

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            # flash an error message if the username already exists
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

    return render_template('auth/register.html')

@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    #authenticate regular users with session management
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            flash('Invalid credentials!', 'danger')
            return redirect(url_for('user_login'))

        login_user(user)
        return redirect(url_for('user_dashboard'))

    return render_template('auth/user_login.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    # authenticate admin users with session management
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        admin = Admin.query.filter_by(username=username).first()
        if not admin or not check_password_hash(admin.password, password):
            flash('Invalid admin credentials!', 'danger')
            return redirect(url_for('admin_login'))

        login_user(admin)
        return redirect(url_for('admin_dashboard'))

    return render_template('auth/admin_login.html')

@app.route('/logout')
@login_required
def logout():
    # log out the current user
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('home'))

# -------------------------
# Admin Management Routes
# -------------------------
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    # render the admin dashboard
    return render_template('admin/dashboard.html')

# Subject Management
@app.route('/admin/subjects', methods=['GET', 'POST'])
@admin_required
def manage_subjects():
    # manage subjects with CRUD operations
    # GET: Display all subjects
    # POST: Create new subject with form data
    if request.method == 'POST':
        new_subject = Subject(
            name=request.form.get('subject_name'),
            description=request.form.get('subject_desc')
        )
        db.session.add(new_subject)
        db.session.commit()
        flash('New subject created!', 'success')
        return redirect(url_for('manage_subjects'))
    
    subjects = Subject.query.order_by(Subject.id).all()
    return render_template('admin/subjects.html', subjects=subjects)

@app.route('/admin/subjects/<int:subject_id>/delete', methods=['POST'])
@admin_required
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted!', 'success')
    return redirect(url_for('manage_subjects'))

# Chapter Management
@app.route('/admin/chapters', methods=['GET', 'POST'])
@admin_required
def manage_chapters():
    if request.method == 'POST':
        new_chapter = Chapter(
            name=request.form.get('chapter_name'),
            description=request.form.get('chapter_desc'),
            subject_id=request.form.get('subject_id')
        )
        db.session.add(new_chapter)
        db.session.commit()
        flash('New chapter added!', 'success')
        return redirect(url_for('manage_chapters'))
    
    chapters = Chapter.query.join(Subject).order_by(Chapter.id).all()
    subjects = Subject.query.all()
    return render_template('admin/chapters.html', chapters=chapters, subjects=subjects)

@app.route('/admin/chapters/<int:chapter_id>/delete', methods=['POST'])
@admin_required
def delete_chapter(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    db.session.delete(chapter)
    db.session.commit()
    flash('Chapter deleted!', 'success')
    return redirect(url_for('manage_chapters'))

# Quiz Management
@app.route('/admin/quizzes', methods=['GET', 'POST'])
@admin_required
def manage_quizzes():
    # manage quizzes with CRUD operations
    if request.method == 'POST':
        try:
            # Convert HH:MM to minutes
            hours, mins = map(int, request.form.get('duration').split(':'))
            total_mins = hours * 60 + mins
            
            new_quiz = Quiz(
                chapter_id=request.form.get('chapter_id'),
                remarks=request.form.get('remarks'),
                start_time=datetime.now(timezone.utc),
                duration=total_mins
            )
            db.session.add(new_quiz)
            db.session.commit()
            flash('Quiz created with time constraints', 'success')
        except ValueError:
            flash('Invalid duration format (use HH:MM)', 'danger')
        return redirect(url_for('manage_quizzes'))
    
    quizzes = Quiz.query.join(Chapter).order_by(Quiz.id).all()
    return render_template('admin/quizzes.html', quizzes=quizzes, chapters=Chapter.query.all())

@app.route('/admin/quizzes/<int:quiz_id>/delete', methods=['POST'])
@admin_required
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    flash('Quiz deleted!', 'success')
    return redirect(url_for('manage_quizzes'))

# Question Management
@app.route('/admin/questions', methods=['GET', 'POST'])
@admin_required
def manage_questions():
    if request.method == 'POST':
        new_question = Question(
            quiz_id=request.form.get('quiz_id'),
            question_statement=request.form.get('question'),
            option1=request.form.get('option1'),
            option2=request.form.get('option2'),
            option3=request.form.get('option3'),
            option4=request.form.get('option4'),
            correct_option=int(request.form.get('correct_option'))
        )
        db.session.add(new_question)
        db.session.commit()
        flash('New question added!', 'success')
        return redirect(url_for('manage_questions'))
    
    questions = Question.query.join(Quiz).order_by(Question.id).all()
    quizzes = Quiz.query.all()
    return render_template('admin/questions.html', questions=questions, quizzes=quizzes)

@app.route('/admin/questions/<int:question_id>/delete', methods=['POST'])
@admin_required
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted!', 'success')
    return redirect(url_for('manage_questions'))

# -------------------------
# User Routes
# -------------------------
@app.route('/user/dashboard')
@login_required
def user_dashboard():
    quizzes = Quiz.query.join(Chapter).join(Subject).all()
    return render_template('user/dashboard.html', quizzes=quizzes)

@app.route('/quiz/<int:quiz_id>/start', methods=['GET', 'POST'])
@login_required
def start_quiz(quiz_id):
    #Quiz Attempt System
    #GET: Display quiz questions
    #POST: Process answers and calculate score
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    if not quiz.is_active():
        flash('This quiz is not currently available', 'danger')
        return redirect(url_for('user_dashboard'))
    if request.method == 'POST':
        # Server-side time validation
        if datetime.now(timezone.utc) > quiz.end_time:
            flash('Quiz time has expired!', 'danger')
            return redirect(url_for('user_dashboard'))

        # Score calculation
        total_score = sum(
            1 for question in questions 
            if request.form.get(f'question_{question.id}') 
            and int(request.form.get(f'question_{question.id}')) == question.correct_option
        )

        # Save score
        new_score = Score(
            quiz_id=quiz.id,
            user_id=current_user.id,
            total_scored=total_score,
            time_stamp_of_attempt=datetime.now(timezone.utc)
        )
        db.session.add(new_score)
        db.session.commit()
        flash(f'You scored {total_score}/{len(questions)}!', 'success')
        return redirect(url_for('user_dashboard'))

    # Store end time in session for client-side validation
    session['quiz_end'] = quiz.end_time.timestamp()
    return render_template('user/quiz_attempt.html', quiz=quiz, questions=questions)

# -------------------------
# API Endpoints
# -------------------------
@app.route('/api/subjects', methods=['GET'])
def api_subjects():
    subjects = Subject.query.all()
    return jsonify([{
        'id': s.id,
        'name': s.name,
        'description': s.description
    } for s in subjects])

@app.route('/api/scores/<int:user_id>', methods=['GET'])
@admin_required
def api_user_scores(user_id):
    scores = Score.query.filter_by(user_id=user_id).all()
    return jsonify([{
        'quiz_id': s.quiz_id,
        'score': s.total_scored,
        'timestamp': s.time_stamp_of_attempt.isoformat()
    } for s in scores])

# -------------------------
# Search & Profile Routes
# -------------------------
@app.route('/admin/search', methods=['GET'])
@admin_required
def admin_search():
    search_term = request.args.get('q', '')
    search_type = request.args.get('type', 'users')
    results = []

    if search_term:
        if search_type == 'users':
            results = User.query.filter(
                (User.username.ilike(f'%{search_term}%')) |
                (User.full_name.ilike(f'%{search_term}%'))
            ).all()
        elif search_type == 'subjects':
            results = Subject.query.filter(
                Subject.name.ilike(f'%{search_term}%')
            ).all()
        elif search_type == 'quizzes':
            results = Quiz.query.join(Chapter).filter(
                Quiz.remarks.ilike(f'%{search_term}%')
            ).all()
        elif search_type == 'questions':
            results = Question.query.filter(
                Question.question_statement.ilike(f'%{search_term}%')
            ).all()

    return render_template('admin/search_results.html',
                         search_term=search_term,
                         search_type=search_type,
                         results=results)

@app.route('/search', methods=['GET'])
@login_required
def user_search():
    search_term = request.args.get('q', '')
    results = {
        'subjects': Subject.query.filter(Subject.name.ilike(f'%{search_term}%')).all(),
        'quizzes': Quiz.query.join(Chapter).join(Subject).filter(
            (Quiz.remarks.ilike(f'%{search_term}%')) |
            (Chapter.name.ilike(f'%{search_term}%')) |
            (Subject.name.ilike(f'%{search_term}%'))
        ).all()
    }
    return render_template('user/search_results.html',
                         search_term=search_term,
                         results=results)

# -------------------------
# Profile Management
# -------------------------
@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and allowed_file(file.filename):
                filename = f"{current_user.id}_{datetime.now(timezone.utc).timestamp()}.{secure_filename(file.filename).split('.')[-1]}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                current_user.avatar = filename
        
        current_user.bio = request.form.get('bio', current_user.bio)
        current_user.location = request.form.get('location', current_user.location)
        current_user.website = request.form.get('website', current_user.website)
        
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('view_profile', username=current_user.username))

    return render_template('user/profile_edit.html')

@app.route('/profile/<username>')
@login_required
def view_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user/profile.html', 
                         user=user,
                         is_own_profile=(user.id == current_user.id))

# -------------------------
# Helper Functions
# -------------------------
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    # Check if the file extension is in the allowed set
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# -------------------------
# Data Visualization Routes
# -------------------------
@app.route('/stats/quiz_analytics')
@admin_required
def quiz_analytics():
    """Generate data for admin quiz statistics"""
    quizzes = Quiz.query.all()
    data = {
        'labels': [q.remarks for q in quizzes],
        'attempts': [len(q.scores) for q in quizzes],
        'average_scores': [round(sum(s.total_scored for s in q.scores)/len(q.scores), 1) 
                          if q.scores else 0 for q in quizzes]
    }
    return jsonify(data)

@app.route('/stats/question_stats/<int:quiz_id>')
@admin_required
def question_stats(quiz_id):
    """Generate question-level statistics for a quiz"""
    quiz = Quiz.query.get_or_404(quiz_id)
    return jsonify([
        {
            'question_id': q.id,
            'correct_percentage': round(
                (sum(1 for s in quiz.scores if s.total_scored == q.correct_option)/len(quiz.scores))*100, 1
            ) if quiz.scores else 0
        } for q in quiz.questions
    ])

@app.route('/user/performance')
@login_required
def user_performance():
    """Generate user's historical performance data"""
    scores = Score.query.filter_by(user_id=current_user.id).order_by(Score.time_stamp_of_attempt).all()
    return jsonify({
        'labels': [s.quiz.remarks for s in scores],
        'scores': [s.total_scored for s in scores],
        'timestamps': [s.time_stamp_of_attempt.isoformat() for s in scores]
    })


# -------------------------
# Error Handlers
# -------------------------
@app.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(403)
def forbidden(error):
    return render_template('errors/403.html'), 403

@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500

@app.errorhandler(500)
def internal_error(error):
    # For chart data endpoints
    if request.path.startswith('/stats'):
        return jsonify({"error": "Failed to load chart data"}), 500
    return render_template('errors/500.html'), 500
