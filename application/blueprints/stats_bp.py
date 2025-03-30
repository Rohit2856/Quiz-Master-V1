from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from application.models import Quiz, Score
from application.decorators import admin_required

stats_bp = Blueprint('stats', __name__, url_prefix='/stats')

# -------------------------
# Data Visualization Routes
# -------------------------
@stats_bp.route('/quiz_analytics')
@admin_required
def quiz_analytics():
    # Generate data for admin quiz statistics
    quizzes = Quiz.query.all()
    return jsonify({
        'labels': [q.remarks for q in quizzes],
        'attempts': [len(q.scores) for q in quizzes],
        'average_scores': [
            round(sum(s.total_scored for s in q.scores)/len(q.scores), 1) 
            if q.scores else 0 
            for q in quizzes
        ]
    })

@stats_bp.route('/question_stats/<int:quiz_id>')
@admin_required
def question_stats(quiz_id):
    # Generate question-level statistics for a quiz
    quiz = Quiz.query.get_or_404(quiz_id)
    return jsonify([{
        'question_id': q.id,
        'correct_percentage': round(
            (sum(1 for s in quiz.scores if s.total_scored == q.correct_option)/len(quiz.scores))*100, 1
        ) if quiz.scores else 0
    } for q in quiz.questions])

@stats_bp.route('/user/performance')
@login_required
def user_performance():
    # Generate user's historical performance data
    scores = Score.query.filter_by(user_id=current_user.id) \
                      .order_by(Score.time_stamp_of_attempt).all()
    return jsonify({
        'labels': [s.quiz.remarks for s in scores],
        'scores': [s.total_scored for s in scores],
        'timestamps': [s.time_stamp_of_attempt.isoformat() for s in scores]
    })