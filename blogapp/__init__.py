from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from flask_ckeditor import CKEditor
from flask_mail import Mail
from blogapp.config import Config


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
# If a user tries to access a route that requires login, then they will be redirected to the login page.
login_manager.login_view = "users.login"
login_manager.login_message_category = "primary"

ckeditor = CKEditor()
mail = Mail()

from blogapp.models import User, Post, Comment, Subscriber, Reply, Newsletter


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    ckeditor.init_app(app)

    with app.app_context():
        db.create_all()

    from blogapp.users.routes import users
    from blogapp.posts.routes import posts
    from blogapp.main.routes import main
    from blogapp.newsletters.routes import newsletters

    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(newsletters)

    return app
