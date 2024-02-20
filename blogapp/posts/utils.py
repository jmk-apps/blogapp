from flask import abort, current_app
from flask_login import current_user
from html_sanitizer import Sanitizer
from functools import wraps
from PIL import Image, ImageOps
import secrets
import os


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # if the user does not have admin status, then return abort with 403 error
        if current_user.is_anonymous:
            return abort(403)
        if current_user.admin is False:
            return abort(403)
        return f(*args, **kwargs)

    return decorated_function


# Allowed Tags for the html-sanitizer
Tags = {
    "a", "h1", "h2", "h3", "strong", "em", "p", "ul", "ol",
    "li", "br", "sub", "sup", "hr", "img",
}

# Set up the sanitizer to allow the tags specified in the "Tags" variable.
# It also will allow img
# tags as img tags are not allowed by default
sanitizer = Sanitizer({
    "tags": Tags,
    "attributes": {
        "a": ("href", "name", "target", "title", "id", "rel"),
        "img": {"alt", "src"}
    },
    "empty": {"hr", "a", "br", "img"},
})


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
