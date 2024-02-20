from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import InputRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired


class NewsletterForm(FlaskForm):
    subject = StringField('Subject', validators=[InputRequired()])
    message = TextAreaField('Message', validators=[InputRequired()])
    newsletter_file = FileField("Newsletter", validators=[FileAllowed(['pdf']), FileRequired()])
    submit = SubmitField('Create')


class UpdateNewsletterForm(FlaskForm):
    subject = StringField('Subject', validators=[InputRequired()])
    message = TextAreaField('Message', validators=[InputRequired()])
    newsletter_file = FileField("Newsletter", validators=[FileAllowed(['pdf'])])
    submit = SubmitField('Update')
