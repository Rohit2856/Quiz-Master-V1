from flask import Blueprint, render_template, request
from flask_login import current_user
from application.models import User, Subject, Quiz, Question
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('home.html')

from flask import Blueprint, render_template, request
from flask_login import current_user
from application.models import User, Subject, Quiz, Question

@main_bp.route('/search', methods=['GET'])
def search():
    search_term = request.args.get('q', '').strip()

    # If no search term show empty 
    if not search_term:
        return render_template('search_results.html', 
                               search_term=search_term,
                               results={})

    # If user is authenticated and admin search users, subjects, quizzes, and questions
    if current_user.is_authenticated and current_user.is_admin:
        matched_users = User.query.filter(User.username.ilike(f'%{search_term}%')).all()
        matched_subjects = Subject.query.filter(Subject.name.ilike(f'%{search_term}%')).all()
        matched_quizzes = Quiz.query.filter(Quiz.quiz_name.ilike(f'%{search_term}%')).all()
        matched_questions = Question.query.filter(Question.question_statement.ilike(f'%{search_term}%')).all()

        results = {
            'users': matched_users,
            'subjects': matched_subjects,
            'quizzes': matched_quizzes,
            'questions': matched_questions
        }
    else:
        # If not admin, only search subjects & quizzes
        matched_subjects = Subject.query.filter(Subject.name.ilike(f'%{search_term}%')).all()
        matched_quizzes = Quiz.query.filter(Quiz.quiz_name.ilike(f'%{search_term}%')).all()

        results = {
            'subjects': matched_subjects,
            'quizzes': matched_quizzes
        }

    return render_template('search_results.html', 
                           search_term=search_term, 
                           results=results)