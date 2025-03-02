from flask import current_app as app
from flask import (render_template, request, redirect, url_for, flash, session, abort)
from flask_login import login_user, login_required, logout_user, current_user
from .database import db
from application.models import User, Admin, Quiz, Chapter, Subject, Question, Score
from application.database import initialize_default_admin 
from application.decorators import admin_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import abort, request
import os
@app.route('/initialize_db')
def initialize_db():
    with app.app_context():
        db.drop_all() # will drop all existing database tables
        db.create_all() # will create new database tables from models.py
        initialize_default_admin() 
    return "Database initialized!"


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
@admin_required
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
    
    # list of chapters with subjects
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
    
    # create quiz form
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
    
    # list quizzes with chapters
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
    
    # create question
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
    
    # list questions with quizzes
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
    try:
        if not isinstance(current_user, User):
            abort(403)
        quizzes = Quiz.query.join(Chapter).join(Subject).all()
        return render_template('user/dashboard.html', quizzes=quizzes)
    except Exception as e:
        app.logger.error(f"Error in user_dashboard: {str(e)}")
        abort(500)

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
        # to calculate score
        total_score = 0
        for question in questions:
            user_answer = request.form.get(f'question_{question.id}')
            if user_answer and int(user_answer) == question.correct_option:
                total_score += 1

        # to save score to database
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

    # to fetch user's past quiz attempts and scores
    scores = Score.query.filter_by(user_id=current_user.id).join(Quiz).join(Chapter).join(Subject).all()
    return render_template('user/scores.html', scores=scores)


@app.route('/user/performance', methods=['GET'])
@login_required
def user_performance():
    """Display user's quiz performance with detailed statistics"""
    if not isinstance(current_user, User):
        abort(403)

    # to get all attempts ordered by latest first
    attempts = Score.query.filter_by(user_id=current_user.id)\
                         .order_by(Score.time_stamp_of_attempt.desc())\
                         .all()

    performance_data = []
    total_correct = 0
    total_questions = 0
    subject_stats = {}

    for attempt in attempts:
        quiz = Quiz.query.get(attempt.quiz_id)
        chapter = Chapter.query.get(quiz.chapter_id)
        subject = Subject.query.get(chapter.subject_id)
        questions = Question.query.filter_by(quiz_id=quiz.id).all()
        
        # to calculate attempt percentage
        attempt_percent = (attempt.total_scored / len(questions)) * 100 if questions else 0
        
        # to update total
        total_correct += attempt.total_scored
        total_questions += len(questions)
        
        # to update subject statistic
        if subject.name not in subject_stats:
            subject_stats[subject.name] = {
                'total_attempts': 0,
                'total_correct': 0,
                'total_questions': 0
            }
        subject_stats[subject.name]['total_attempts'] += 1
        subject_stats[subject.name]['total_correct'] += attempt.total_scored
        subject_stats[subject.name]['total_questions'] += len(questions)

        performance_data.append({
            'date': attempt.time_stamp_of_attempt.strftime('%d %b %Y %H:%M'),
            'subject': subject.name,
            'chapter': chapter.name,
            'score': f"{attempt.total_scored}/{len(questions)}",
            'percentage': round(attempt_percent, 1)
        })

    # calculate overall statistics
    overall_percentage = (total_correct / total_questions * 100) if total_questions > 0 else 0
    subject_breakdown = []
    
    for subject, stats in subject_stats.items():
        sub_percent = (stats['total_correct'] / stats['total_questions'] * 100) if stats['total_questions'] > 0 else 0
        subject_breakdown.append({
            'name': subject,
            'attempts': stats['total_attempts'],
            'accuracy': round(sub_percent, 1)
        })

    return render_template('user/performance.html',
                         attempts=performance_data,
                         total_attempts=len(attempts),
                         overall_score=f"{total_correct}/{total_questions}",
                         overall_percentage=round(overall_percentage, 1),
                         subjects=subject_breakdown)


@app.route('/admin/search', methods=['GET'])
@login_required
def admin_search():
    if not isinstance(current_user, Admin):
        abort(403)
    
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
        'subjects': [],
        'quizzes': []
    }

    if search_term:
        results['subjects'] = Subject.query.filter(
            Subject.name.ilike(f'%{search_term}%')
        ).all()
        
        results['quizzes'] = Quiz.query.join(Chapter).join(Subject).filter(
            (Quiz.remarks.ilike(f'%{search_term}%')) |
            (Chapter.name.ilike(f'%{search_term}%')) |
            (Subject.name.ilike(f'%{search_term}%'))
        ).all()

    return render_template('user/search_results.html',
                         search_term=search_term,
                         results=results)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        # to handle file upload
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and allowed_file(file.filename):
                filename = f"{current_user.id}_{datetime.now().timestamp()}.{secure_filename(file.filename).split('.')[-1]}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                current_user.avatar = filename
        
        # to update other fields
        current_user.bio = request.form.get('bio', current_user.bio)
        current_user.location = request.form.get('location', current_user.location)
        current_user.website = request.form.get('website', current_user.website)
        
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('view_profile', username=current_user.username))

    return render_template('profile/edit.html')

@app.route('/profile/<username>')
@login_required
def view_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('profile/view.html', 
                         user=user,
                         is_own_profile=(user.id == current_user.id))

@app.route('/admin/users')
@admin_required
def manage_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/user/<int:user_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    return '', 204  # No content for requests