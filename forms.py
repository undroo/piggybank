# forms.py

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators, DecimalField, IntegerField
from wtforms.validators import DataRequired, NumberRange

class RegisterForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Email()])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm_password', message='Passwords must match')
    ])
    confirm_password = PasswordField('Confirm Password')
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    email = StringField('Email', [validators.Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class GoalForm(FlaskForm):
    name = StringField('Goal Name', validators=[DataRequired()])
    savings_goal = DecimalField('Savings Goal ($)', validators=[DataRequired(), NumberRange(min=0)])
    participants = IntegerField('Number of Participants', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Add Goal')

class SearchGoalForm(FlaskForm):
    goal_id = StringField('Goal ID', validators=[DataRequired()])
    submit = SubmitField('Search Goal')

class DeleteGoalForm(FlaskForm):
    submit = SubmitField('Delete Goal')