from werkzeug.utils import secure_filename
from flask import current_app
import os

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_file(file):
    """Secure file upload handling"""
    if not file:
        return None
    filename = secure_filename(file.filename)
    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
    return filename

def calculate_score(quiz, submitted_answers):
    """Score calculation logic (newly added)"""
    return sum(
        1 for question in quiz.questions
        if str(submitted_answers.get(f'question_{question.id}')) == str(question.correct_option)
    )

def delete_file(filename):
    """Secure file deletion with error handling"""
    if not filename:
        return False

    try:
        upload_folder = current_app.config['UPLOAD_FOLDER']
        file_path = os.path.join(upload_folder, filename)
        
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        current_app.logger.error(f"File deletion failed: {str(e)}")
        return False