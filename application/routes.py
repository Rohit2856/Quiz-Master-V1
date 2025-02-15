from flask import current_app as app
from flask import (render_template, request, redirect, url_for, flash, session, abort)
from flask_login import login_user, login_required, logout_user, current_user
from .database import db
from application.models import User, Admin 
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

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

#  Creation of Admin Dashboard Home
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not isinstance(current_user, Admin):
        abort(403)
    return render_template('admin/dashboard.html')

# -------------------------
# Subject Management
# -------------------------
@app.route('/admin/subjects', methods=['GET', 'POST'])
@login_required
def manage_subjects():
    if not isinstance(current_user, Admin):
        abort(403)
    
    # Create Subject
    if request.method == 'POST':
        new_subject = Subject(
            name=request.form.get('subject_name'),
            description=request.form.get('subject_desc')
        )
        db.session.add(new_subject)
        db.session.commit()
        flash('New subject created!', 'success')
        return redirect(url_for('manage_subjects'))
    
    # List of subjects
    subjects = Subject.query.order_by(Subject.id).all()
    return render_template('admin/subjects.html', subjects=subjects)

@app.route('/admin/subjects/<int:subject_id>/delete', methods=['POST'])
@login_required
def delete_subject(subject_id):
    if not isinstance(current_user, Admin):
        abort(403)
    
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted!', 'success')
    return redirect(url_for('manage_subjects'))

# -------------------------
# Chapter Management
# -------------------------
@app.route('/admin/chapters', methods=['GET', 'POST'])
@login_required
def manage_chapters():
    if not isinstance(current_user, Admin):
        abort(403)
    
    # Create new chapter
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
    
    # List of chapters with subjects
    chapters = Chapter.query.join(Subject).order_by(Chapter.id).all()
    subjects = Subject.query.all()
    return render_template('admin/chapters.html', 
                         chapters=chapters, 
                         subjects=subjects)

@app.route('/admin/chapters/<int:chapter_id>/delete', methods=['POST'])
@login_required
def delete_chapter(chapter_id):
    if not isinstance(current_user, Admin):
        abort(403)
    
    chapter = Chapter.query.get_or_404(chapter_id)
    db.session.delete(chapter)
    db.session.commit()
    flash('Chapter deleted!', 'success')
    return redirect(url_for('manage_chapters'))

# -------------------------
# Quiz Management
# -------------------------
@app.route('/admin/quizzes', methods=['GET', 'POST'])
@login_required
def manage_quizzes():
    if not isinstance(current_user, Admin):
        abort(403)
    
    # Create quiz form
    if request.method == 'POST':
        new_quiz = Quiz(
            chapter_id=request.form.get('chapter_id'),
            time_duration=request.form.get('duration'),
            remarks=request.form.get('remarks')
        )
        db.session.add(new_quiz)
        db.session.commit()
        flash('New quiz created!', 'success')
        return redirect(url_for('manage_quizzes'))
    
    # List quizzes with chapters
    quizzes = Quiz.query.join(Chapter).order_by(Quiz.id).all()
    chapters = Chapter.query.all()
    return render_template('admin/quizzes.html', 
                         quizzes=quizzes, 
                         chapters=chapters)

@app.route('/admin/quizzes/<int:quiz_id>/delete', methods=['POST'])
@login_required
def delete_quiz(quiz_id):
    if not isinstance(current_user, Admin):
        abort(403)
    
    quiz = Quiz.query.get_or_404(quiz_id)
    db.session.delete(quiz)
    db.session.commit()
    flash('Quiz deleted!', 'success')
    return redirect(url_for('manage_quizzes'))

# -------------------------
# Question Management
# -------------------------
@app.route('/admin/questions', methods=['GET', 'POST'])
@login_required
def manage_questions():
    if not isinstance(current_user, Admin):
        abort(403)
    
    # Create question
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
    
    # List questions with quizzes
    questions = Question.query.join(Quiz).order_by(Question.id).all()
    quizzes = Quiz.query.all()
    return render_template('admin/questions.html', 
                         questions=questions, 
                         quizzes=quizzes)

@app.route('/admin/questions/<int:question_id>/delete', methods=['POST'])
@login_required
def delete_question(question_id):
    if not isinstance(current_user, Admin):
        abort(403)
    
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted!', 'success')
    return redirect(url_for('manage_questions'))

# -------------------------
# User Dashboard
# -------------------------
@app.route('/user/dashboard', endpoint='user_dashboard')
@login_required
def user_dashboard():
    if not isinstance(current_user, User):  # Ensure only regular users can access
        abort(403)

    # Fetch all available quizzes with their associated chapters and subjects
    quizzes = Quiz.query.join(Chapter).join(Subject).all()
    return render_template('user/dashboard.html', quizzes=quizzes)

# -------------------------
# Quiz attempt system
# -------------------------
@app.route('/quiz/<int:quiz_id>/start', methods=['GET', 'POST'])
@login_required
def start_quiz(quiz_id):
    if not isinstance(current_user, User):
        abort(403)

    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    if request.method == 'POST':
        # Calculate score
        total_score = 0
        for question in questions:
            user_answer = request.form.get(f'question_{question.id}')
            if user_answer and int(user_answer) == question.correct_option:
                total_score += 1

        # Save score to database
        new_score = Score(
            quiz_id=quiz.id,
            user_id=current_user.id,
            total_scored=total_score,
            time_stamp_of_attempt=datetime.utcnow()  # Ensure you import datetime
        )
        db.session.add(new_score)
        db.session.commit()

        flash(f'You scored {total_score}/{len(questions)}!', 'success')
        return redirect(url_for('user_dashboard'))

    return render_template('user/quiz.html', quiz=quiz, questions=questions)

# -------------------------
# View quiz scores
# -------------------------
@app.route('/user/scores')
@login_required
def view_scores():
    if not isinstance(current_user, User):
        abort(403)

    # Fetch user's past quiz attempts and scores
    scores = Score.query.filter_by(user_id=current_user.id).join(Quiz).join(Chapter).join(Subject).all()
    return render_template('user/scores.html', scores=scores)

