from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from application import db
from application.models import Quiz, Score, Subject
from application.utils import calculate_score
from datetime import datetime, timedelta  

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/dashboard')
@login_required
def dashboard():
    
    # Fetch all quizzes then filter out the ended ones
    all_quizzes = Quiz.query.all()
    available_quizzes = [quiz for quiz in all_quizzes if quiz.status in ("Active", "Upcoming")]

    # Fetch past scores (attempt history)
    past_scores = Score.query.filter_by(user_id=current_user.id)\
                             .order_by(Score.time_stamp_of_attempt.desc())\
                             .all()
    total_attempts = len(past_scores)

    # Query subjects for performance overview 
    subjects = Subject.query.all()

    return render_template(
        'user/dashboard.html',
        all_quizzes=available_quizzes,
        past_scores=past_scores,
        total_attempts=total_attempts,
        subjects=subjects,
        user=current_user
    )

@user_bp.route('/quiz/<int:quiz_id>/attempt', methods=['GET', 'POST'])
@login_required
def attempt_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    current_time = datetime.now()
    computed_end_time = quiz.end_time or (quiz.start_time + timedelta(minutes=quiz.duration))
    
    # Prevent accessing upcoming quizzes
    if current_time < quiz.start_time:
        flash(f'Quiz opens at {quiz.start_time.strftime("%d %b %Y, %I:%M %p")}', 'warning')
        return redirect(url_for('user.dashboard'))

    existing_score = Score.query.filter_by(quiz_id=quiz_id, user_id=current_user.id).first()
    if existing_score:
        flash('Already attempted', 'info')
        return redirect(url_for('user.results', quiz_id=quiz_id))

    if request.method == 'POST':
        if datetime.now() > computed_end_time:
            flash('Quiz expired!', 'danger')
            return redirect(url_for('user.dashboard'))
        
        try:
            total_score = calculate_score(quiz, request.form)
            user_answers = {
                question.id: int(request.form.get(f"question_{question.id}"))
                for question in quiz.questions
                if request.form.get(f"question_{question.id}")
            }
            
            new_score = Score(
                quiz_id=quiz.id,
                user_id=current_user.id,
                total_scored=total_score,
                time_stamp_of_attempt=datetime.now(),
                answers=user_answers
            )
            db.session.add(new_score)
            db.session.commit()
            
            flash(f'Score: {total_score}/{len(quiz.questions)}', 'success')
            return redirect(url_for('user.results', quiz_id=quiz.id))
        
        except Exception as e:
            db.session.rollback()
            flash('Submission failed', 'danger')
            return redirect(url_for('user.dashboard'))

    session['quiz_start_time'] = datetime.now().timestamp()
    return render_template(
        'user/quiz_attempt.html',
        quiz=quiz,
        questions=quiz.questions,
        end_time=computed_end_time,
        is_active=current_time <= computed_end_time)


@user_bp.route('/quiz/<int:quiz_id>/results')
@login_required
def results(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    score = Score.query.filter_by(
        quiz_id=quiz_id,
        user_id=current_user.id
    ).order_by(Score.time_stamp_of_attempt.desc()).first()
    
    if not score:
        flash('No attempt found for this quiz', 'warning')
        return redirect(url_for('user.dashboard'))
        
    raw_answers = score.answers  # string representation of the dictionary
    # Convert keys to int
    user_answers = {int(k): v for k, v in raw_answers.items()}

    return render_template(
        'user/results.html',
        quiz=quiz,
        score=score,
        user_answers=user_answers
    )



@user_bp.route('/summary')
@login_required
def summary():
    # Get all subjects
    subjects = Subject.query.all()
    
    # Get past scores for the current user in chronological order
    past_scores = Score.query.filter_by(user_id=current_user.id)\
                             .order_by(Score.time_stamp_of_attempt.asc())\
                             .all()

    # build data for subject-wise performance chart
    subject_labels = [subject.name for subject in subjects]
    subject_avg_scores = []
    for subject in subjects:
        # filter score for this subject
        subject_scores = [score.total_scored for score in past_scores 
                          if score.quiz.chapter.subject.id == subject.id]
        avg = sum(subject_scores) / len(subject_scores) if subject_scores else 0
        subject_avg_scores.append(avg)
    
    # build data for quiz score chart using quiz_name instead of remarks
    quiz_labels = [
        f"{score.quiz.quiz_name} - {score.quiz.chapter.subject.name}"
        for score in past_scores
    ] if past_scores else []
    quiz_scores = [score.total_scored for score in past_scores] if past_scores else []
    
    # build subject max scores dictionary: key = subject name; value = {max_score, quiz_name}
    subject_max_scores = {}
    for score in past_scores:
        subject_name = score.quiz.chapter.subject.name
        if subject_name not in subject_max_scores or score.total_scored > subject_max_scores[subject_name]["max_score"]:
            subject_max_scores[subject_name] = {
                "max_score": score.total_scored,
                "quiz_name": score.quiz.quiz_name}
    
    return render_template(
        'user/summary.html',
        subjects=subjects,
        past_scores=past_scores,
        total_attempts=len(past_scores),
        subject_labels=subject_labels,
        subject_avg_scores=subject_avg_scores,
        quiz_labels=quiz_labels,
        quiz_scores=quiz_scores,
        subject_max_scores=subject_max_scores)

@user_bp.route('/attempt-history')
@login_required
def attempt_history():
    past_scores = Score.query.filter_by(user_id=current_user.id)\
                             .order_by(Score.time_stamp_of_attempt.desc())\
                             .all()
    
    return render_template(
        'user/attempt_history.html',
        past_scores=past_scores)


@user_bp.route('/scores')
@login_required
def scores():
    past_scores = Score.query.filter_by(user_id=current_user.id)\
                             .order_by(Score.time_stamp_of_attempt.desc())\
                             .all()
    return render_template('user/scores.html', scores=past_scores)