from flask_login import current_user
from wtforms.fields.simple import TextAreaField

from blogapp import db
from blogapp.models import User
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_ckeditor import CKEditorField
from wtforms import StringField, EmailField, PasswordField, SubmitField, BooleanField, SelectField
from wtforms.validators import InputRequired, Length, Email, EqualTo, ValidationError

CATEGORY_CHOICES = [
    'Please select a category',
    'Travel',
    'Technology',
    'Books',
    'Activities',
    'Work'
]


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


class PostForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    subtitle = StringField('Subtitle', validators=[InputRequired()])
    category = SelectField('Category', choices=CATEGORY_CHOICES, validators=[InputRequired()])
    content = CKEditorField('Content', validators=[InputRequired()])
    post_pic = FileField("Post Picture", validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Post')

    def validate_category(self, category):
        if category.data == 'Please select a category':
            raise ValidationError('Please select a category')


class CommentForm(FlaskForm):
    content = TextAreaField('Write a comment', validators=[InputRequired()])
    submit = SubmitField('Post')


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

