from flask import flash
from flask import Blueprint, jsonify, redirect, request, url_for
from flask_login import login_required, current_user
from application.models import User, Subject, Quiz, Question

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Error handlers here...
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

@api_bp.route('/search', methods=['GET'])
@login_required

def api_search():
    search_term = request.args.get('q', '').strip()
    # Check if the user is authenticated
    if not current_user.is_authenticated:
        flash("Please login first.", "warning")  # Flash a warning message
        return redirect(url_for('auth.user_login'))
    
    search_term = request.args.get('q', '').strip()
    if not search_term:
        return jsonify({}), 200

    if current_user.is_admin:
        matched_users = User.query.filter(User.username.ilike(f'%{search_term}%')).all()
        matched_subjects = Subject.query.filter(Subject.name.ilike(f'%{search_term}%')).all()
        matched_quizzes = Quiz.query.filter(Quiz.quiz_name.ilike(f'%{search_term}%')).all()
        matched_questions = Question.query.filter(Question.question_statement.ilike(f'%{search_term}%')).all()

        results = {
            'users': [{
                'id': u.id,
                'username': u.username,
                'email': u.email
            } for u in matched_users],
            'subjects': [{
                'id': s.id,
                'name': s.name,
                'description': s.description
            } for s in matched_subjects],
            'quizzes': [{
                'id': q.id,
                'quiz_name': q.quiz_name
            } for q in matched_quizzes],
            'questions': [{
                'id': ques.id,
                'question_statement': ques.question_statement,
                'quiz_id': ques.quiz_id   # Ensure quiz_id is included
            } for ques in matched_questions]
        }
    else:
        matched_subjects = Subject.query.filter(Subject.name.ilike(f'%{search_term}%')).all()
        matched_quizzes = Quiz.query.filter(Quiz.quiz_name.ilike(f'%{search_term}%')).all()

        results = {
            'subjects': [{
                'id': s.id,
                'name': s.name,
                'description': s.description
            } for s in matched_subjects],
            'quizzes': [{
                'id': q.id,
                'quiz_name': q.quiz_name
            } for q in matched_quizzes]
        }

    return jsonify(results), 200

