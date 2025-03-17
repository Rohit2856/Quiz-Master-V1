from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from application import db
from application.models import Subject, Chapter, Quiz, Question, User
from application.forms import SubjectForm, ChapterForm, QuizForm, QuestionForm
from application.decorators import admin_required
from application.utils import save_file, delete_file
from datetime import datetime, timezone
from werkzeug.utils import secure_filename
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# -------------------------------------------
# Dashboard & Search Routes & User Management
# -------------------------------------------
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard with system overview"""
    stats = {
        'users': User.query.count(),
        'subjects': Subject.query.count(),
        'quizzes': Quiz.query.count(),
        'questions': Question.query.count()
    }
    return render_template('admin/dashboard.html', stats=stats)

@admin_bp.route('/search')
@admin_required
def admin_search():
    """Unified search functionality"""
    search_term = request.args.get('q', '')
    search_type = request.args.get('type', 'users')
    results = []

    if search_term:
        search_map = {
            'users': User.query.filter(User.username.ilike(f'%{search_term}%')),
            'subjects': Subject.query.filter(Subject.name.ilike(f'%{search_term}%')),
            'quizzes': Quiz.query.join(Chapter).filter(Quiz.remarks.ilike(f'%{search_term}%')),
            'questions': Question.query.filter(Question.question_statement.ilike(f'%{search_term}%'))
        }
        results = search_map.get(search_type, []).all()

    return render_template('admin/search_results.html')

@admin_bp.route('/users')
@admin_required
def manage_users():
    """User management for admins"""
    users = User.query.order_by(User.username).all()
    return render_template('admin/manage_users.html', users=users)

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete a user"""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully', 'success')
    return redirect(url_for('admin.manage_users'))

# -------------------------
# Subject Management
# -------------------------
@admin_bp.route('/subjects', methods=['GET', 'POST'])
@admin_required
def manage_subjects():
    """Subject CRUD operations with file upload"""
    form = SubjectForm()
    
    if form.validate_on_submit():
        try:
            subject = Subject(
                name=form.name.data,
                description=form.description.data
            )
            db.session.add(subject)
            db.session.commit()
            flash('Subject created successfully', 'success')
            return redirect(url_for('admin.manage_subjects'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating subject: {str(e)}', 'danger')

    subjects = Subject.query.order_by(Subject.name).all()
    return render_template('admin/manage_subjects.html', 
                         form=form, 
                         subjects=subjects)

@admin_bp.route('/subjects/<int:subject_id>/delete', methods=['POST'])
@admin_required
def delete_subject(subject_id):
    """Delete subject with related chapters"""
    subject = Subject.query.get_or_404(subject_id)
    try:
        db.session.delete(subject)
        db.session.commit()
        flash('Subject deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting subject: {str(e)}', 'danger')
    return redirect(url_for('admin.manage_subjects'))

# -------------------------
# Chapter Management
# -------------------------
@admin_bp.route('/chapters/<int:subject_id>', methods=['GET', 'POST'])
@admin_required
def manage_chapters(subject_id):
    """Chapter management for specific subject"""
    form = ChapterForm()
    subject = Subject.query.get_or_404(subject_id)
    
    if form.validate_on_submit():
        try:
            chapter = Chapter(
                name=form.name.data,
                description=form.description.data,
                subject_id=subject.id
            )
            db.session.add(chapter)
            db.session.commit()
            flash('Chapter added successfully', 'success')
            return redirect(url_for('admin.manage_chapters', subject_id=subject.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating chapter: {str(e)}', 'danger')

    return render_template('admin/manage_chapters.html',
                         form=form,
                         subject=subject)

@admin_bp.route('/chapters/<int:chapter_id>/delete', methods=['POST'])
@admin_required
def delete_chapter(chapter_id):
    """Delete chapter with related quizzes"""
    chapter = Chapter.query.get_or_404(chapter_id)
    try:
        db.session.delete(chapter)
        db.session.commit()
        flash('Chapter deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting chapter: {str(e)}', 'danger')
    return redirect(url_for('admin.manage_chapters', subject_id=chapter.subject_id))

# -------------------------
# Quiz Management
# -------------------------
@admin_bp.route('/quizzes/<int:chapter_id>', methods=['GET', 'POST'])
@admin_required
def manage_quizzes(chapter_id):
    """Quiz management for specific chapter"""
    form = QuizForm()
    chapter = Chapter.query.get_or_404(chapter_id)
    form.chapter_id.choices = [(chapter.id, chapter.name)]

    if form.validate_on_submit():
        try:
            new_quiz = Quiz(
                chapter_id=chapter.id,
                start_time=form.start_time.data,
                duration=form.get_duration_minutes(),
                remarks=form.remarks.data
            )
            db.session.add(new_quiz)
            db.session.commit()
            flash('Quiz created successfully', 'success')
            return redirect(url_for('admin.manage_quizzes', chapter_id=chapter.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating quiz: {str(e)}', 'danger')

    return render_template('admin/manage_quizzes.html',
                         form=form,
                         chapter=chapter)

@admin_bp.route('/quizzes/<int:quiz_id>/delete', methods=['POST'])
@admin_required
def delete_quiz(quiz_id):
    """Delete quiz with related questions"""
    quiz = Quiz.query.get_or_404(quiz_id)
    try:
        db.session.delete(quiz)
        db.session.commit()
        flash('Quiz deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting quiz: {str(e)}', 'danger')
    return redirect(url_for('admin.manage_quizzes', chapter_id=quiz.chapter_id))

# -------------------------
# Question Management
# -------------------------
@admin_bp.route('/questions/<int:quiz_id>', methods=['GET', 'POST'])
@admin_required
def manage_questions(quiz_id):
    """Question management for specific quiz"""
    form = QuestionForm()
    quiz = Quiz.query.get_or_404(quiz_id)

    if form.validate_on_submit():
        try:
            question = Question(
                quiz_id=quiz.id,
                question_statement=form.question_statement.data,
                option1=form.option1.data,
                option2=form.option2.data,
                option3=form.option3.data,
                option4=form.option4.data,
                correct_option=form.correct_option.data
            )
            db.session.add(question)
            db.session.commit()
            flash('Question added successfully', 'success')
            return redirect(url_for('admin.manage_questions', quiz_id=quiz.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating question: {str(e)}', 'danger')

    return render_template('admin/manage_questions.html',
                         form=form,
                         quiz=quiz)

@admin_bp.route('/questions/<int:question_id>/delete', methods=['POST'])
@admin_required
def delete_question(question_id):
    """Delete individual question"""
    question = Question.query.get_or_404(question_id)
    quiz_id = question.quiz_id
    try:
        db.session.delete(question)
        db.session.commit()
        flash('Question deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting question: {str(e)}', 'danger')
    return redirect(url_for('admin.manage_questions', quiz_id=quiz_id))
