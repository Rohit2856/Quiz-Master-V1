from flask_wtf import FlaskForm
from wtforms import (
    DateField, HiddenField, StringField, TextAreaField, SelectField,
    DateTimeLocalField, PasswordField, BooleanField, FileField, SubmitField, URLField)
from wtforms.validators import DataRequired, Length, Regexp, EqualTo, Email, URL, Optional
from flask_wtf.file import FileAllowed, FileField

class LoginForm(FlaskForm):
    """Form for user login"""
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')  

class SubjectForm(FlaskForm):
    """Form for creating/editing subjects"""
    name = StringField('Subject Name', validators=[
        DataRequired(),
        Length(min=2, max=100)])
    description = TextAreaField('Description', validators=[
        Length(max=500)])
    submit = SubmitField('Save Subject')  

class ChapterForm(FlaskForm):

    name = StringField('Chapter Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Length(max=500)])
    subject_id = SelectField('Subject',coerce=int,validators=[DataRequired()])
    submit = SubmitField('Save Chapter')

class QuizForm(FlaskForm):
    quiz_id = HiddenField('Quiz ID')
    quiz_name = StringField('Quiz Name', validators=[DataRequired()])
    start_time = DateTimeLocalField(
        'Start Time',
        format='%Y-%m-%dT%H:%M',
        validators=[DataRequired()])
    duration = StringField(
        'Duration (HH:MM)',
        validators=[
            DataRequired(),
            Regexp(r'^\d{2}:\d{2}$', message="Use HH:MM format")])
    remarks = TextAreaField('Remarks')
    chapter_id = SelectField('Chapter', coerce=int)  # Make sure this exists
    submit = SubmitField('Save Quiz')


class QuestionForm(FlaskForm):
    
    question_statement = TextAreaField('Question', validators=[
        DataRequired(),
        Length(max=500)])
    option1 = StringField('Option 1', validators=[
        DataRequired(),
        Length(max=200)])
    option2 = StringField('Option 2', validators=[
        DataRequired(),
        Length(max=200)])
    option3 = StringField('Option 3', validators=[
        Length(max=200)])
    option4 = StringField('Option 4', validators=[
        Length(max=200)])
    correct_option = SelectField(
        'Correct Answer',
        choices=[(1,'Option 1'),(2,'Option 2'),(3,'Option 3'),(4,'Option 4')],
        coerce=int,
        validators=[DataRequired()])
    submit = SubmitField('Save Question') 

class UserRegistrationForm(FlaskForm):
    # Form for user registration
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=4, max=25)])
    email = StringField('Email', validators=[
        DataRequired(),
        Email(message="Invalid email format")])  
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8),
        Regexp(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$',
               message="Must contain letters and numbers"),
        EqualTo('confirm', message="Passwords must match")])
    confirm = PasswordField('Repeat Password', validators=[DataRequired()])
    full_name = StringField('Full Name', validators=[
        DataRequired(),
        Length(min=2, max=50)])
    qualification = StringField('Qualification')
    dob = DateField(
        'Date of Birth',
        format='%Y-%m-%d',
        validators=[DataRequired()])  
    avatar = FileField('Profile Picture', validators=[
        FileAllowed(['jpg', 'png', 'gif'], 'Images only!')])
    submit = SubmitField('Register')
    
class AdminLoginForm(FlaskForm):
     """Form for admin login"""
     username = StringField('Username',validators=[ DataRequired(), Length(min=4,max=25)])     
     password = PasswordField('Password',validators=[DataRequired()])     
     submit = SubmitField('Login')  

class ProfileForm(FlaskForm):
    full_name = StringField('Full Name', validators=[Optional()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    bio = TextAreaField('Biography', validators=[Optional()])
    dob = DateField('Date of Birth', format='%Y-%m-%d', validators=[Optional()])
    qualification = StringField('Qualifications')
    location = StringField('Location', validators=[Optional()])
    website = URLField('Website', validators=[Optional(), URL()])
    avatar = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Save Changes')
    remove_avatar = BooleanField('Remove current photo', default=False)

