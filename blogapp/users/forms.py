from blogapp import db
from blogapp.models import User
from flask_wtf import FlaskForm
from flask_login import current_user
from wtforms import StringField, SubmitField, EmailField, PasswordField, BooleanField
from wtforms.validators import InputRequired, ValidationError, Length, EqualTo, Email
from flask_wtf.file import FileField, FileAllowed


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)])
    email = EmailField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=16)])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(),
                                                                     EqualTo('password',
                                                                             message='Password and Confirm Password must match')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = db.session.execute(db.select(User).where(User.username == username.data)).scalar()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = db.session.execute(db.select(User).where(User.email == email.data)).scalar()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=20)])
    email = EmailField('Email', validators=[InputRequired(), Email()])
    profile_pic = FileField("Update Profile Picture", validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = db.session.execute(db.select(User).where(User.username == username.data)).scalar()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = db.session.execute(db.select(User).where(User.email == email.data)).scalar()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


class RequestResetForm(FlaskForm):
    email = EmailField('Email', validators=[InputRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = db.session.execute(db.select(User).where(User.email == email.data)).scalar()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=16)])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(),
                                                                     EqualTo('password',
                                                                             message='Password and Confirm Password must match')])
    submit = SubmitField('Reset Password')
