from flask_wtf import FlaskForm
from wtforms import StringField, EmailField, PasswordField
from wtforms.fields.simple import SubmitField
from wtforms.validators import InputRequired, Length, Email, EqualTo


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)])
    email = EmailField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(),
                                                                     EqualTo('password', message='Password and Confirm Password must match')])
    submit = SubmitField('Sign Up')

