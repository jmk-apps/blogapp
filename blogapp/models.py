from blogapp import db, login_manager
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from flask_login import UserMixin


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

    # Relationship with post
    posts: Mapped[list["Post"]] = relationship(back_populates="author")

    # Relationship with comments
    comments: Mapped[list["Comment"]] = relationship(back_populates="comment_author")


class Post(db.Model):
    __tablename__ = 'post'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    subtitle: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    post_pic: Mapped[str] = mapped_column(String(50), nullable=False, default="default_post_pic.jpg")
    date_posted: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now(timezone.utc))

    # Relationship with user
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    author: Mapped["User"] = relationship(back_populates="posts")

    # Relationship with comment
    comments: Mapped[list["Comment"]] = relationship(back_populates="parent_post")


class Comment(db.Model):
    __tablename__ = 'comment'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    date_posted: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now(timezone.utc))

    # Relationship with user
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    comment_author: Mapped["User"] = relationship(back_populates="comments")

    # Relationship with post
    post_id: Mapped[int] = mapped_column(ForeignKey("post.id"), nullable=False)
    parent_post: Mapped["Post"] = relationship(back_populates="comments")
