from flask_wtf import FlaskForm
from flask_ckeditor import CKEditorField
from wtforms import StringField, SubmitField, SelectField, TextAreaField
from wtforms.validators import InputRequired, ValidationError
from flask_wtf.file import FileField, FileAllowed

CATEGORY_CHOICES = [
    'Please select a category',
    'Travel',
    'Technology',
    'Books',
    'Activities',
    'Work'
]


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
