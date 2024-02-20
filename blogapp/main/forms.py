from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, TextAreaField
from wtforms.validators import InputRequired, Email


class SearchForm(FlaskForm):
    content = StringField('Content', validators=[InputRequired()])
    submit = SubmitField('Search')


class ContactUsForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    email = EmailField('Email', validators=[InputRequired(), Email()])
    message = TextAreaField('Message', validators=[InputRequired()])
    submit = SubmitField('Send')
