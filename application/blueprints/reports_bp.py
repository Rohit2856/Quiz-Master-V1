from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from application import db
from application.models import QuizAttempt, User, Quiz

reports_bp = Blueprint(
    'reports', 
    __name__,
    url_prefix='/reports',
    template_folder='templates/reports'
)

@reports_bp.route('/')
@login_required
def reports_dashboard():
    """Main reports dashboard"""
    return render_template('reports/dashboard.html')

@reports_bp.route('/user-progress')
@login_required
def user_progress_report():
    """Individual user progress report"""
    user_id = request.args.get('user_id', current_user.id)
    attempts = QuizAttempt.query.filter_by(user_id=user_id).all()
    return render_template('reports/user_progress.html', attempts=attempts)

@reports_bp.route('/question-analytics')
@login_required
def question_analytics():
    """Question performance analytics"""
    quiz_id = request.args.get('quiz_id')
    questions = Quiz.query.get(quiz_id).questions if quiz_id else []
    
    analytics = []
    for question in questions:
        analytics.append({
            'id': question.id,
            'text': question.question_statement[:50] + "...",
            'correct_percent': question.correct_attempts_percentage(),
            'common_errors': question.most_common_errors()
        })
    
    return render_template('reports/question_analytics.html', 
                         analytics=analytics)

@reports_bp.route('/export')
@login_required
def export_reports():
    """Export report data"""
    report_type = request.args.get('type', 'csv')
    
    if report_type == 'csv':
        return jsonify({"status": "CSV export started"})
    
    return jsonify({"error": "Invalid export type"}), 400

@reports_bp.route('/real-time')
@login_required
def real_time_analytics():
    """Real-time quiz statistics"""
    active_quizzes = Quiz.query.filter(Quiz.end_time > db.func.now()).all()
    return render_template('reports/real_time.html', 
                         active_quizzes=active_quizzes)

# Error Handling
@reports_bp.errorhandler(404)
def report_not_found(error):
    return render_template('reports/404.html'), 404
