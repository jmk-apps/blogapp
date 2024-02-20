from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
from flask_ckeditor import CKEditor
from flask_mail import Mail
import os


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
login_manager.login_view = "users.login"
login_manager.login_message_category = "primary"

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DB_URI')

# Used for Flask-Mail
app.config['MAIL_SERVER'] = "smtp.gmail.com"
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get("EMAIL_USER")
app.config['MAIL_PASSWORD'] = os.environ.get("EMAIL_PASS")

db.init_app(app)
login_manager.init_app(app)
ckeditor = CKEditor(app)
mail = Mail(app)
from blogapp.models import User, Post, Comment, Subscriber, Reply, Newsletter

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

