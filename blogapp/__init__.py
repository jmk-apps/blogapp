from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_login import LoginManager
import os


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.login_message_category = "primary"

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DB_URI')
db.init_app(app)
login_manager.init_app(app)
from blogapp.models import User, Post
from blogapp import routes


with app.app_context():
    db.create_all()
