from blogapp import app, db
from flask import render_template, redirect, url_for, flash, request, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from blogapp.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, CommentForm
from blogapp.models import User, Post, Comment, Reply
from flask_login import login_user, logout_user, login_required, current_user
import os
import secrets
from PIL import Image, ImageOps
from html_sanitizer import Sanitizer
from datetime import datetime, timezone


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


@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    posts = db.paginate(db.select(Post).order_by(Post.date_posted.desc()), page=page, per_page=3)
    return render_template("index.html", posts=posts)


@app.route('/about')
def about():
    return render_template("about.html", title="About")


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


@app.route('/account', methods=["GET", "POST"])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.profile_pic.data:
            delete_picture(current_user.profile_pic, "profile")
            picture_name = save_picture(form.profile_pic.data, "profile")
            current_user.profile_pic = picture_name
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash("Your account has been updated!", "success")
        return redirect(url_for('account'))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    profile_picture = url_for('static', filename=f'profile_pics/{current_user.profile_pic}')
    return render_template("account.html", form=form, image_file=profile_picture, title="Account")


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been created! You can now login', 'success')
        return redirect(url_for('login'))
    return render_template("register.html", form=form, title="Register")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.execute(db.select(User).where(User.email == form.email.data)).scalar()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template("login.html", form=form, title="Login")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/post/new", methods=['GET', 'POST'])
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
            date_posted=datetime.now(timezone.utc)
        )
        if form.post_pic.data:
            picture_name = save_picture(form.post_pic.data, "post")
            post_new.post_pic = picture_name
        db.session.add(post_new)
        db.session.commit()
        flash('Your post has been created!', "success")
        return redirect(url_for('home'))

    return render_template("create_edit_post.html", form=form, title="New Post", legend="New Post")


@app.route('/post/<int:post_id>', methods=["GET", "POST"])
def show_post(post_id):
    post = db.get_or_404(Post, post_id)
    form = CommentForm()
    # The CommentForm is used for the reply form because their structure the same.
    reply_form = CommentForm()

    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('You must login or register to comment', "danger")
            return redirect(url_for('login'))
        new_comment = Comment(
            content=form.content.data,
            comment_author=current_user,
            parent_post=post,
            date_posted=datetime.now(timezone.utc)
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('show_post', post_id=post.id))
    num_comments = len(post.comments)
    return render_template("post.html", post=post, form=form, reply_form=reply_form, num_comments=num_comments, title="Post")


@app.route('/reply/<int:comment_id>', methods=["POST"])
def new_reply(comment_id):
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
        return redirect(url_for('show_post', post_id=comment.post_id))
    return redirect(url_for('show_post', post_id=comment.post_id))




@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
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
        return redirect(url_for('show_post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.subtitle.data = post.subtitle
        form.category.data = post.category
        form.content.data = post.content
    post_picture = url_for('static', filename=f'post_pics/{post.post_pic}')

    return render_template("create_edit_post.html", form=form, title="Update Post", image_file=post_picture,
                           legend="Update Post")


@app.route('/post/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    post = db.get_or_404(Post, post_id)
    delete_picture(post.post_pic, "post")
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', "success")
    return redirect(url_for('home'))


@app.route('/contact')
def contact():
    return render_template("contact.html", title="Contact")


