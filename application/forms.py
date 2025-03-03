from flask_wtf import FlaskForm
from wtforms import DateTimeLocalField, StringField
from wtforms.validators import DataRequired, Regexp

class QuizForm(FlaskForm):
    start_time = DateTimeLocalField('Start Time', 
                                  format='%Y-%m-%dT%H:%M',
                                  validators=[DataRequired()])
    duration = StringField('Duration (HH:MM)',
                          validators=[
                              DataRequired(),
                              Regexp(r'^\d{1,2}:\d{2}$', 
                                    message="Use hours:minutes format (e.g., 01:30)")
                          ])