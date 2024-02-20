from flask import current_app, abort
from blogapp import db, mail
from blogapp.models import Subscriber
from flask_mail import Message
import os
import secrets
from datetime import datetime, timezone
from functools import wraps
from flask_login import current_user


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # if the user does not have admin status, then return abort with 403 error
        if current_user.admin is False:
            return abort(403)
        return f(*args, **kwargs)

    return decorated_function


def save_newsletter_file(news_letter_file):
    # Get the filename and path
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(news_letter_file.filename)
    newsletter_fn = random_hex + f_ext

    picture_path = os.path.join(current_app.root_path, 'static/newsletters', newsletter_fn)
    news_letter_file.save(picture_path)

    return newsletter_fn


def delete_newsletter_file(news_letter_file):
    file_path = os.path.join(current_app.root_path, 'static/newsletters', news_letter_file)
    os.remove(file_path)


def send_newsletter_email(newsletter):
    subscribers = db.session.execute(db.select(Subscriber)).scalars().all()
    if subscribers:
        with mail.connect() as conn:
            for subscriber in subscribers:
                msg = Message(sender="kagandajohn762@gmail.com",
                              recipients=[subscriber.email],
                              subject=newsletter.subject,
                              body=newsletter.message
                              )
                os.path.join(current_app.root_path, 'static/newsletters', newsletter.newsletter_file)
                with current_app.open_resource(
                        os.path.join(current_app.root_path, 'static/newsletters', newsletter.newsletter_file)) as fp:
                    msg.attach(newsletter.newsletter_file, f"{newsletter.newsletter_file}/pdf", fp.read())
                conn.send(msg)
        newsletter.date_email = datetime.now(timezone.utc)
        return True
    else:
        return False
