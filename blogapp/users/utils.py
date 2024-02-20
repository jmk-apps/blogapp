from flask import current_app, abort, url_for
from blogapp import mail, app
from itsdangerous.url_safe import URLSafeTimedSerializer
from flask_login import current_user
from functools import wraps
import os
import secrets
from PIL import Image, ImageOps
from flask_mail import Message
import re


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # if the user does not have admin status, then return abort with 403 error
        if current_user.admin is False:
            return abort(403)
        return f(*args, **kwargs)

    return decorated_function


def save_picture(form_picture, type):
    # Get the filename and path
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    if type == "profile":
        picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)
    else:
        picture_path = os.path.join(current_app.root_path, 'static/post_pics', picture_fn)

    # Resize and save the picture
    if type == "profile":
        output_size = (250, 250)
    else:
        output_size = (1000, 800)

    with Image.open(form_picture) as img:
        ImageOps.cover(img, output_size).save(picture_path)

    return picture_fn


def delete_picture(picture_name, type):
    if picture_name != "default_profile_pic.jpg" and type == "profile":
        picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_name)
        os.remove(picture_path)
    elif picture_name != "default_post_pic.jpg" and type == "post":
        picture_path = os.path.join(current_app.root_path, 'static/post_pics', picture_name)
        os.remove(picture_path)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender="kagandajohn762@gmail.com", recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('users.reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


def send_subscriber_email(email):
    s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    token = s.dumps({'email': email})
    msg = Message('Subscribe Request', sender="kagandajohn762@gmail.com", recipients=[email])
    msg.body = f'''To subscribe to the monthly newsletter, visit the following link:
{url_for('users.subscribe_token', token=token, _external=True)}
The link will expire after 3 minutes.
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


def validate_subscriber_email(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if re.fullmatch(regex, email):
        return True
    else:
        return False


def verify_subscribe_token(token, expires=180):
    s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = s.loads(token, max_age=expires)['email']
    except:
        return None
    return email
