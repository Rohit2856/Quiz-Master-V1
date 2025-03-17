from flask import request 
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from application import db
from application.models import Subject, Score, Quiz, Question, User
from application.decorators import admin_required
from datetime import datetime, timezone

# To initialize blueprint first
api_bp = Blueprint('api', __name__, url_prefix='/api')

# --------------
# Error Handlers 
# --------------
@api_bp.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@api_bp.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized'}), 401

@api_bp.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Forbidden'}), 403

@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@api_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# -------------
# API Endpoints
# -------------
@api_bp.route('/subjects', methods=['GET'])
@login_required
def api_subjects():
    """Get all subjects in JSON format"""
    subjects = Subject.query.all()
    return jsonify([{
        "id": s.id,
        "name": s.name,
        "description": s.description
    } for s in subjects])

@api_bp.route('/scores/<int:user_id>', methods=['GET'])
@admin_required
def api_user_scores(user_id):
    """Get quiz scores for specific user (admin only)"""
    scores = Score.query.filter_by(user_id=user_id).all()
    return jsonify([{
        "quiz_id": s.quiz_id,
        "score": s.total_scored,
        "timestamp": s.time_stamp_of_attempt.isoformat()
    } for s in scores])

@api_bp.route('/quiz/<int:quiz_id>/questions', methods=['GET'])
@login_required
def get_quiz_questions(quiz_id):
    """Get quiz questions in JSON format"""
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if not quiz.is_active():
        return jsonify({'error': 'Quiz unavailable'}), 403
        
    return jsonify({
        "quiz_id": quiz.id,
        "remarks": quiz.remarks,
        "duration": quiz.duration,
        "questions": [{
            "id": q.id,
            "question": q.question_statement,
            "options": [q.option1, q.option2, q.option3, q.option4],
            "correct_option": q.correct_option
        } for q in quiz.questions]
    })

@api_bp.route('/quiz/<int:quiz_id>/submit', methods=['POST'])
@login_required
def api_submit_quiz(quiz_id):
    """Submit quiz answers via API"""
    quiz = Quiz.query.get_or_404(quiz_id)
    data = request.get_json()
    
    if datetime.now(timezone.utc) > quiz.end_time:
        return jsonify({'error': 'Quiz time has expired'}), 403
