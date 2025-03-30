from flask import Blueprint, render_template, request, redirect, url_for, flash 
from application import db
from application.models import Subject, Chapter, Quiz, Question, User, Score
from application.forms import SubjectForm, ChapterForm, QuizForm, QuestionForm
from application.decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# -------------------------------------------
# Dashboard & Search Routes & User Management
# -------------------------------------------
@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    # Display a dashboard
    stats = {
        'users': User.query.count(),
        'subjects': Subject.query.count(),
        'quizzes': Quiz.query.count(),
        'questions': Question.query.count()}
    return render_template('admin/dashboard.html', stats=stats)

@admin_bp.route('/users')
@admin_required
def manage_users():
    # Display all users in the system  
    users = User.query.order_by(User.username).all()
    return render_template('admin/manage_users.html', users=users)

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    # Delete a user
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
    # Displays all subjects and allows creating/editing each subject..
    form = SubjectForm()

    if request.method == "POST":
        subject_id = request.form.get("subject_id")
        name = form.name.data
        description = form.description.data

        if subject_id:  # EDIT existing subject
            subject_to_edit = Subject.query.get_or_404(subject_id)
            subject_to_edit.name = name
            subject_to_edit.description = description
            db.session.commit()
            flash("Subject updated successfully!", "success")
        else:  # CREATE new subject
            existing_subject = Subject.query.filter_by(name=name).first()
            if existing_subject:
                flash("Subject already exists!", "warning")
            else:
                new_subject = Subject(name=name, description=description)
                db.session.add(new_subject)
                db.session.commit()
                flash("Subject created successfully!", "success")

        return redirect(url_for('admin.manage_subjects'))

    # GET request => show all subjects
    subjects = Subject.query.order_by(Subject.name).all()
    return render_template('admin/manage_subjects.html', form=form, subjects=subjects)


@admin_bp.route('/subjects/<int:subject_id>/delete', methods=['POST'])
@admin_required
def delete_subject(subject_id):
    # Delete a subject
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

@admin_bp.route('/admin/chapters/<int:subject_id>', methods=['GET', 'POST'])
def manage_chapters(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    form = ChapterForm(request.form) # Initialize the form

    # Provide the choice
    form.subject_id.choices = [(subject.id, subject.name)]

    if request.method == "POST":
        print("DEBUG: raw form data =", request.form)
        print("DEBUG: validate_on_submit =", form.validate())
        print("DEBUG: form.errors =", form.errors)
        print("DEBUG: form.name.data =", form.name.data)

        if form.validate():
            chapter_id = request.form.get("chapter_id", "").strip()
            if chapter_id:
                # Edit existing
                chapter = Chapter.query.get_or_404(chapter_id)
                chapter.name = form.name.data
                chapter.description = form.description.data
                flash("Chapter updated successfully!", "success")
            else:
                # Create new
                new_chapter = Chapter(
                    name=form.name.data,
                    description=form.description.data,
                    subject_id=subject.id
                )
                db.session.add(new_chapter)
                flash("Chapter added successfully!", "success")
            db.session.commit()

            return redirect(url_for('admin.manage_chapters', subject_id=subject_id))

    chapters = Chapter.query.filter_by(subject_id=subject_id).all()
    return render_template(
        'admin/manage_chapters.html',
        subject=subject,
        chapters=chapters,
        form=form)


@admin_bp.route('/chapters/<int:chapter_id>/delete', methods=['POST'])
@admin_required
def delete_chapter(chapter_id):
    # Delete chapter with related quizzes
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
@admin_bp.route('/quizzes/<int:chapter_id>', methods=['GET'])
@admin_required
def manage_quizzes(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    quizzes = Quiz.query.filter_by(chapter_id=chapter.id).all()
    return render_template('admin/manage_quizzes.html',
                           chapter=chapter,
                           quizzes=quizzes)

@admin_bp.route('/chapters/<int:chapter_id>/quizzes/new', methods=['GET', 'POST'])
@admin_required
def create_quiz(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    form = QuizForm()
    form.chapter_id.choices = [(chapter.id, chapter.name)]
    form.chapter_id.data = chapter.id 

    if form.validate_on_submit():
        # Convert the HH:MM duration to total minutes 
        hh, mm = form.duration.data.split(':')
        duration_in_minutes = int(hh) * 60 + int(mm)
        
        new_quiz = Quiz(
            quiz_name=form.quiz_name.data,
            start_time=form.start_time.data.replace(tzinfo=None),
            duration=duration_in_minutes,
            remarks=form.remarks.data,
            chapter_id=chapter.id
        )
        db.session.add(new_quiz)
        db.session.commit()

        flash("Quiz created successfully!", "success")
        return redirect(url_for('admin.manage_quizzes', chapter_id=chapter.id))

    # If GET or validation failed, render the form
    return render_template(
        'admin/quiz_form.html',
        chapter=chapter,
        form=form,
        mode="create")


@admin_bp.route('/chapters/<int:chapter_id>/quizzes/<int:quiz_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_quiz(chapter_id, quiz_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    quiz = Quiz.query.get_or_404(quiz_id)
    
    form = QuizForm(obj=quiz)
    
    form.chapter_id.choices = [(chapter.id, chapter.name)]
    form.chapter_id.data = chapter.id
    
    # On GET, convert the quiz.duration (minutes) to "HH:MM"
    if request.method == 'GET':
        hours = quiz.duration // 60
        mins = quiz.duration % 60
        form.duration.data = f"{hours:02d}:{mins:02d}"

    if form.validate_on_submit():
        # Convert the HH:MM back to minutes
        hh, mm = form.duration.data.split(':')
        quiz.duration = int(hh) * 60 + int(mm)
        
        quiz.quiz_name = form.quiz_name.data
        quiz.start_time = form.start_time.data.replace(tzinfo=None)
        quiz.remarks = form.remarks.data
        
        db.session.commit()
        flash("Quiz updated successfully!", "success")
        return redirect(url_for('admin.manage_quizzes', chapter_id=chapter.id))

    return render_template(
        'admin/quiz_form.html',
        chapter=chapter,
        quiz=quiz,
        form=form,
        mode="edit")


@admin_bp.route('/quizzes/<int:quiz_id>/delete', methods=['POST'])
@admin_required
def delete_quiz(quiz_id):
    # Delete quiz with related questions
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
    # Question management create & edit route.
    form = QuestionForm()
    quiz = Quiz.query.get_or_404(quiz_id)

    if request.method == "POST":
        question_id = request.form.get("question_id")
        question_statement = form.question_statement.data
        option1 = form.option1.data
        option2 = form.option2.data
        option3 = form.option3.data
        option4 = form.option4.data
        correct_option = form.correct_option.data

        try:
            if question_id:
                # to edit existing question
                existing_q = Question.query.get_or_404(question_id)
                existing_q.question_statement = question_statement
                existing_q.option1 = option1
                existing_q.option2 = option2
                existing_q.option3 = option3
                existing_q.option4 = option4
                existing_q.correct_option = correct_option
                db.session.commit()
                flash("Question updated successfully!", "success")
            else:
                # to create new question
                new_q = Question(
                    quiz_id=quiz.id,
                    question_statement=question_statement,
                    option1=option1,
                    option2=option2,
                    option3=option3,
                    option4=option4,
                    correct_option=correct_option
                )
                db.session.add(new_q)
                db.session.commit()
                flash("Question added successfully!", "success")

        except Exception as e:
            db.session.rollback()
            flash(f"Error saving question: {str(e)}", "danger")

        return redirect(url_for('admin.manage_questions', quiz_id=quiz.id))

    # GET request - display questions
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    return render_template(
        'admin/manage_questions.html',
        form=form,
        quiz=quiz,
        questions=questions)


@admin_bp.route('/questions/<int:question_id>/delete', methods=['POST'])
@admin_required
def delete_question(question_id):
    # Delete individual question
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


@admin_bp.route('/attempts')
@admin_required
def view_all_attempts():
    all_attempts = Score.query.order_by(Score.time_stamp_of_attempt.desc()).all()
    return render_template('admin/manage_attempts.html', attempts=all_attempts)

@admin_bp.route('/attempts/<int:score_id>/details')
@admin_required
def view_attempt_details(score_id):
    score_record = Score.query.get_or_404(score_id)

    # Convert raw answers (with string keys) to int keys
    raw_answers = score_record.answers or {}
    user_answers = {int(k): v for k, v in raw_answers.items() if k.isdigit()}

    quiz = score_record.quiz

    return render_template(
        'admin/attempt_details.html',
        score=score_record,
        quiz=quiz,
        user_answers=user_answers)
