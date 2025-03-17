from datetime import datetime, timezone, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db

# Define models for the application 
# User model for storing user details 
# Subject model for storing subject details 
# Chapter model for storing chapter details 
# Quiz model for storing quiz details 
# Question model for storing question details 
# Score model for storing user quiz scores and attempts 
# QuizAttempt model for tracking quiz attempts

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    qualification = db.Column(db.String(100))
    dob = db.Column(db.Date)
    bio = db.Column(db.Text)
    location = db.Column(db.String(100))
    avatar = db.Column(db.String(255), nullable=True)
    website = db.Column(db.String(200))  

    # Security & tracking fields 
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_seen = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships with Score and QuizAttempt models (one-to-many) 
    scores = db.relationship('Score', back_populates='user', cascade='all, delete-orphan')
    quiz_attempts = db.relationship('QuizAttempt', back_populates='user', cascade='all, delete-orphan')

    # Password security methods 
    @property
    def password(self):
        raise AttributeError('Password is not readable')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def update_last_seen(self):
        self.last_seen = datetime.now(timezone.utc)
        db.session.commit()

class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)
    
    # Relationships with Chapter model (one-to-many) 
    chapters = db.relationship('Chapter', back_populates='subject', cascade='all, delete-orphan')

class Chapter(db.Model):
    __tablename__ = 'chapters'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)
    
    # Relationships with Subject and Quiz models (one-to-many) 
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    subject = db.relationship('Subject', back_populates='chapters')
    quizzes = db.relationship('Quiz', back_populates='chapter', cascade='all, delete-orphan')

class Quiz(db.Model):
    __tablename__ = 'quizzes'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # Minutes duration of quiz 
    remarks = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True)
    
    # Relationships with Chapter, Question, Score, and QuizAttempt models (one-to-many) 
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id', ondelete='CASCADE'), nullable=False)
    chapter = db.relationship('Chapter', back_populates='quizzes')
    questions = db.relationship('Question', back_populates='quiz', cascade='all, delete-orphan')
    scores = db.relationship('Score', back_populates='quiz', cascade='all, delete-orphan')
    quiz_attempts = db.relationship('QuizAttempt', back_populates='quiz', cascade='all, delete-orphan')
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=True)
    
    @property
    def is_active(self):
        now = datetime.now(timezone.utc)
        return self.start_time <= now <= self.end_time

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    question_statement = db.Column(db.Text, nullable=False)
    option1 = db.Column(db.String(200), nullable=False)
    option2 = db.Column(db.String(200), nullable=False)
    option3 = db.Column(db.String(200))
    option4 = db.Column(db.String(200))
    correct_option = db.Column(db.Integer, nullable=False)
    
    # Relationships with Quiz model (many-to-one) 
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id', ondelete='CASCADE'), nullable=False)
    quiz = db.relationship('Quiz', back_populates='questions')

class Score(db.Model):
    __tablename__ = 'scores'
    id = db.Column(db.Integer, primary_key=True)
    total_scored = db.Column(db.Integer, nullable=False)
    time_stamp_of_attempt = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships with User and Quiz models (many-to-one) 
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship('User', back_populates='scores')
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id', ondelete='CASCADE'), nullable=False)
    quiz = db.relationship('Quiz', back_populates='scores')
    
    # Composite index for common queries on user and quiz 
    __table_args__ = (
        db.Index('idx_user_quiz', 'user_id', 'quiz_id'),
    )

class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id', ondelete='CASCADE'), nullable=False)
    attempt_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships with User and Quiz models (many-to-one)
    user = db.relationship('User', back_populates='quiz_attempts')
    quiz = db.relationship('Quiz', back_populates='quiz_attempts')
