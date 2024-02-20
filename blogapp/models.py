from blogapp import db, login_manager, app
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from flask_login import UserMixin
from itsdangerous.url_safe import URLSafeTimedSerializer


@login_manager.user_loader
def load_user(user_id):
    return db.session.execute(db.select(User).where(User.id == user_id)).scalar()


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    profile_pic: Mapped[str] = mapped_column(String(50), nullable=False, default="default_profile_pic.jpg")
    password: Mapped[str] = mapped_column(String(250), nullable=False)
    admin: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    date_created: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Relationship with post
    posts: Mapped[list["Post"]] = relationship(back_populates="author", cascade="all, delete-orphan")

    # Relationship with comments
    comments: Mapped[list["Comment"]] = relationship(back_populates="comment_author", cascade="all, delete-orphan")

    # Relationship with replies
    replies: Mapped[list["Reply"]] = relationship(back_populates="reply_author", cascade="all, delete-orphan")

    def get_reset_token(self):
        s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token, expires=1800):
        s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=expires)['user_id']
        except:
            return None
        return db.session.execute(db.select(User).where(User.id == user_id)).scalar()


class Post(db.Model):
    __tablename__ = 'post'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    subtitle: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    post_pic: Mapped[str] = mapped_column(String(50), nullable=False, default="default_post_pic.jpg")
    date_posted: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Relationship with user
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    author: Mapped["User"] = relationship(back_populates="posts")

    # Relationship with comment
    comments: Mapped[list["Comment"]] = relationship(back_populates="parent_post", cascade="all, delete-orphan")


class Comment(db.Model):
    __tablename__ = 'comment'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    date_posted: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Relationship with user
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    comment_author: Mapped["User"] = relationship(back_populates="comments")

    # Relationship with post
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"), nullable=False)
    parent_post: Mapped["Post"] = relationship(back_populates="comments")

    # Relationship with reply
    replies: Mapped[list["Reply"]] = relationship(back_populates="comment_post", cascade="all, delete-orphan")


class Reply(db.Model):
    __tablename__ = 'reply'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    date_posted: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Relationship with user
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    reply_author: Mapped["User"] = relationship(back_populates="replies")

    # Relationship with comment
    comment_id: Mapped[int] = mapped_column(ForeignKey("comment.id"), nullable=False)
    comment_post: Mapped["Comment"] = relationship(back_populates="replies")


class Subscriber(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    date_subscribed: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class Newsletter(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subject: Mapped[str] = mapped_column(String(150), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    newsletter_file: Mapped[str] = mapped_column(String(50), nullable=False, default="default_post_pic.jpg")
    date_created: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    date_emailed: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    author: Mapped[str] = mapped_column(String(30), nullable=False)
