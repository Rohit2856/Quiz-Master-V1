from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from application import db
from application.models import Quiz, Question, Score, Subject, Chapter 
from application.utils import calculate_score
from datetime import datetime, timezone

user_bp = Blueprint('user', __name__, url_prefix='/user')

# -------------------------
# User Routes
# -------------------------
@user_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing available quizzes"""
    
    now = datetime.now(timezone.utc)

    active_quizzes = Quiz.query.filter(
        Quiz.start_time <= now,
        Quiz.end_time >= now
    ).all()  # Ensure the query runs correctly

    return render_template('user/dashboard.html', 
                           active_quizzes=active_quizzes, 
                           user=current_user)

@user_bp.route('/quiz/<int:quiz_id>/attempt', methods=['GET', 'POST'])
@login_required
def attempt_quiz(quiz_id):
    """Handle quiz attempts with time validation"""
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if not quiz.is_active():
        flash('This quiz is no longer available', 'danger')
        return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        if datetime.now(timezone.utc) > quiz.end_time:
            flash('Quiz time has expired!', 'danger')
            return redirect(url_for('user.dashboard'))

        try:
            # Calculate score using utility function
            total_score = calculate_score(quiz, request.form)
            
            new_score = Score(
                quiz_id=quiz.id,
                user_id=current_user.id,
                total_scored=total_score,
                time_stamp_of_attempt=datetime.now(timezone.utc)
            )
            db.session.add(new_score)
            db.session.commit()
            
            flash(f'Scored {total_score}/{len(quiz.questions)}!', 'success')
            return redirect(url_for('user.results', quiz_id=quiz.id))
            
        except Exception as e:
            db.session.rollback()
            flash('Error submitting quiz. Please try again.', 'danger')
            return redirect(url_for('user.dashboard'))

    session['quiz_start_time'] = datetime.now(timezone.utc).timestamp()
    return render_template('user/quiz_attempt.html', 
                         quiz=quiz,
                         questions=quiz.questions)

@user_bp.route('/quiz/<int:quiz_id>/results')
@login_required
def results(quiz_id):
    """Display quiz results"""
    quiz = Quiz.query.get_or_404(quiz_id)
    score = Score.query.filter_by(
        quiz_id=quiz_id, 
        user_id=current_user.id
    ).order_by(Score.time_stamp_of_attempt.desc()).first()
    
    if not score:
        flash('No attempt found for this quiz', 'warning')
        return redirect(url_for('user.dashboard'))
        
    return render_template('user/results.html',
                         quiz=quiz,
                         score=score,
                         questions=quiz.questions)

@user_bp.route('/search', methods=['GET'])
@login_required
def search():
    """Search functionality for user's quiz history"""
    search_term = request.args.get('q', '')
    results = {
        'scores': Score.query.join(Quiz).join(Chapter).join(Subject)
                  .filter(
                      (Subject.name.ilike(f'%{search_term}%')) |
                      (Chapter.name.ilike(f'%{search_term}%')) |
                      (Quiz.remarks.ilike(f'%{search_term}%'))
                  )
                  .filter_by(user_id=current_user.id)
                  .all()
    }
    return render_template('user/search_results.html',
                         search_term=search_term,
                         results=results)
