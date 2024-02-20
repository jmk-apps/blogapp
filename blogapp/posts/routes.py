from flask import render_template, Blueprint, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from blogapp import db
from blogapp.models import Post, Comment, Reply
from blogapp.posts.forms import PostForm, CommentForm
from datetime import datetime, timezone
from blogapp.posts.utils import admin_required, sanitizer, save_picture, delete_picture

posts = Blueprint('posts', __name__)


@posts.route("/post/new", methods=['GET', 'POST'])
@admin_required
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        clean_content = sanitizer.sanitize(form.content.data)
        post_new = Post(
            title=form.title.data,
            subtitle=form.subtitle.data,
            category=form.category.data,
            content=clean_content,
            author=current_user,
            author_username=current_user.username,
            date_posted=datetime.now(timezone.utc)
        )
        if form.post_pic.data:
            picture_name = save_picture(form.post_pic.data, "post")
            post_new.post_pic = picture_name
        db.session.add(post_new)
        db.session.commit()
        flash('Your post has been created!', "success")
        return redirect(url_for('main.home'))

    return render_template("create_edit_post.html", form=form, title="New Post", legend="New Post")


@posts.route('/post/<int:post_id>', methods=["GET", "POST"])
def show_post(post_id):
    post = db.get_or_404(Post, post_id)
    form = CommentForm()
    # The CommentForm is used for the reply form because their structure the same.
    reply_form = CommentForm()

    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('You must login or register to comment.', "danger")
            return redirect(url_for('users.login'))
        new_comment = Comment(
            content=form.content.data,
            comment_author=current_user,
            parent_post=post,
            date_posted=datetime.now(timezone.utc)
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('posts.show_post', post_id=post.id))
    num_comments = len(post.comments)
    return render_template("post.html", post=post, form=form, reply_form=reply_form, num_comments=num_comments,
                           title="Post")


@posts.route('/reply/<int:comment_id>', methods=["POST"])
def new_reply(comment_id):
    if not current_user.is_authenticated:
        flash('You must login or register to reply.', "danger")
        return redirect(url_for('users.login'))
    comment = db.session.execute(db.select(Comment).where(Comment.id == comment_id)).scalar()
    # The CommentForm is used for the reply form because their structure the same.
    reply_form = CommentForm()
    # Note: In the post.html file, in the reply form the novalidate attribute has been removed to prevent
    # the user from submitting an empty reply.This is used
    # because the validation error won't be shown when the user
    # is redirected to the post.html file if validation fails.
    if reply_form.validate_on_submit():
        reply = Reply(
            content=reply_form.content.data,
            date_posted=datetime.now(timezone.utc),
            reply_author=current_user,
            comment_post=comment
        )
        db.session.add(reply)
        db.session.commit()
        return redirect(url_for('posts.show_post', post_id=comment.post_id))
    return redirect(url_for('posts.show_post', post_id=comment.post_id))


@posts.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@admin_required
@login_required
def update_post(post_id):
    post = db.get_or_404(Post, post_id)
    form = PostForm()
    if form.validate_on_submit():
        if form.post_pic.data:
            delete_picture(post.post_pic, "post")
            picture_name = save_picture(form.post_pic.data, "post")
            post.post_pic = picture_name
        post.title = form.title.data
        post.subtitle = form.subtitle.data
        post.category = form.category.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', "success")
        return redirect(url_for('posts.show_post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.subtitle.data = post.subtitle
        form.category.data = post.category
        form.content.data = post.content
    post_picture = url_for('static', filename=f'post_pics/{post.post_pic}')

    return render_template("create_edit_post.html", form=form, title="Update Post", image_file=post_picture,
                           legend="Update Post")


@posts.route('/post/<int:post_id>/delete', methods=['POST'])
@admin_required
@login_required
def delete_post(post_id):
    post = db.get_or_404(Post, post_id)
    delete_picture(post.post_pic, "post")
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', "success")
    return redirect(url_for('main.home'))
