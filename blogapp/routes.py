from blogapp import app, db, mail
from flask import render_template, redirect, url_for, flash, request, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from blogapp.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, CommentForm, RequestResetForm, \
    ResetPasswordForm, NewsletterForm, UpdateNewsletterForm, ContactUsForm
from blogapp.models import User, Post, Comment, Reply, Subscriber, Newsletter
from flask_login import login_user, logout_user, login_required, current_user
import os
import secrets
from PIL import Image, ImageOps
from html_sanitizer import Sanitizer
from datetime import datetime, timezone, timedelta
from flask_mail import Message
from itsdangerous.url_safe import URLSafeTimedSerializer
import re

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
            password=hashed_password,
            date_created=datetime.now(timezone.utc)
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
    return render_template("post.html", post=post, form=form, reply_form=reply_form, num_comments=num_comments,
                           title="Post")


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


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender="kagandajohn762@gmail.com", recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    form = RequestResetForm()
    if form.validate_on_submit():
        user = db.session.execute(db.select(User).where(User.email == form.email.data)).scalar()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password', 'primary')
        return redirect(url_for('login'))
    return render_template("reset_request.html", form=form, title="Reset Password")


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token.', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template("reset_token.html", form=form, title="Reset Password")


categories = [
    'Travel',
    'Technology',
    'Books',
    'Activities',
    'Work'
]

archives = [
    "2024",
    "2023",
    "2022",
    "2021",
    "2020"
]


@app.route('/search', methods=['GET', 'POST'])
def search():
    stmt = db.select(Post).order_by(Post.date_posted.desc())
    page = request.args.get('page', 1, type=int)
    param = request.args.get("param")

    search_value = request.form.get("search")
    if search_value:
        stmt = db.select(Post).where(Post.content.icontains(search_value)).order_by(Post.date_posted.desc())
    elif param in categories:
        stmt = db.select(Post).filter_by(category=param).order_by(Post.date_posted.desc())
    elif param in archives:
        stmt = db.select(Post).where(Post.date_posted.icontains(param)).order_by(Post.date_posted.desc())

    posts = db.paginate(stmt, page=page, per_page=3)
    return render_template("search.html", param_value=param, search_value=search_value, posts=posts, title="Search")


def send_subscriber_email(email):
    s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    token = s.dumps({'email': email})
    msg = Message('Subscribe Request', sender="kagandajohn762@gmail.com", recipients=[email])
    msg.body = f'''To subscribe to the monthly newsletter, visit the following link:
{url_for('subscribe_token', token=token, _external=True)}
The link will expire after 3 minutes.
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


def validate_email(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
    if re.fullmatch(regex, email):
        return True
    else:
        return False


@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe_request():
    email = request.form.get('email')
    if validate_email(email):
        subscriber = db.session.execute(db.select(Subscriber).where(Subscriber.email == email)).scalar()
        if subscriber:
            flash('That email is already included in the subscriber list.', 'success')
            return redirect(url_for('home'))
        send_subscriber_email(email)
        flash('An email has been sent with instructions to subscribe to the monthly newsletter', 'primary')
        return redirect(url_for('home'))
    else:
        flash('The email entered was invalid, please enter a valid email', 'danger')
        return redirect(url_for('home'))


def verify_subscribe_token(token, expires=180):
    s = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = s.loads(token, max_age=expires)['email']
    except:
        return None
    return email


@app.route('/subscribe/<token>', methods=['GET', 'POST'])
def subscribe_token(token):
    subscriber_email = verify_subscribe_token(token)
    current_subscriber_email = db.session.execute(
        db.select(Subscriber).where(Subscriber.email == subscriber_email)).scalar()
    if subscriber_email is None or current_subscriber_email:
        flash('That is an invalid or expired token.', 'warning')
        return redirect(url_for('home'))
    new_subscriber = Subscriber(
        email=subscriber_email,
        date_subscribed=datetime.now(timezone.utc)
    )
    db.session.add(new_subscriber)
    db.session.commit()
    flash('Your have successfully subscribed to our monthly newsletter', 'success')
    return redirect(url_for('home'))


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


@app.route('/newsletter/new', methods=['GET', 'POST'])
@login_required
def new_newsletter():
    form = NewsletterForm()
    if form.validate_on_submit():
        newsletter_fn = save_newsletter_file(form.newsletter_file.data)
        newsletter_new = Newsletter(
            subject=form.subject.data,
            message=form.message.data,
            author=current_user.username,
            date_created=datetime.now(timezone.utc),
            newsletter_file=newsletter_fn
        )
        db.session.add(newsletter_new)
        db.session.commit()
        flash("Your newsletter has been created!", "success")
        return redirect(url_for('newsletter_home'))

    return render_template("create_edit_newsletter.html", form=form, legend="New Newsletter", title="New Newsletter")


@app.route('/newsletter/<int:newsletter_id>', methods=['GET', 'POST'])
@login_required
def newsletter(newsletter_id):
    newsletter = db.get_or_404(Newsletter, newsletter_id)
    return render_template("newsletter.html", legend="Newsletter", newsletter=newsletter, title="Newsletter")


@app.route('/newsletter/<int:newsletter_id>/update', methods=['GET', 'POST'])
@login_required
def update_newsletter(newsletter_id):
    newsletter = db.get_or_404(Newsletter, newsletter_id)
    form = UpdateNewsletterForm()
    if form.validate_on_submit():
        if form.newsletter_file.data:
            delete_newsletter_file(newsletter.newsletter_file)
            file_name = save_newsletter_file(form.newsletter_file.data)
            newsletter.newsletter_file = file_name
        newsletter.subject = form.subject.data
        newsletter.message = form.message.data
        db.session.commit()
        flash("Your newsletter has been updated!", "success")
        return redirect(url_for('newsletter', newsletter_id=newsletter.id))
    elif request.method == 'GET':
        form.subject.data = newsletter.subject
        form.message.data = newsletter.message
    newsletter_fn = newsletter.newsletter_file

    return render_template("create_edit_newsletter.html", form=form, letter_id=newsletter.id,
                           newsletter_file=newsletter_fn, legend="Update Newsletter", title="Update Newsletter")


@app.route('/newsletter/<int:newsletter_id>/delete', methods=['POST'])
@login_required
def delete_newsletter(newsletter_id):
    newsletter = db.get_or_404(Newsletter, newsletter_id)
    delete_newsletter_file(newsletter.newsletter_file)
    db.session.delete(newsletter)
    db.session.commit()
    flash("Your newsletter has been deleted!", "success")
    return redirect(url_for("newsletter_home"))


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


@app.route('/newsletter/<int:newsletter_id>/email', methods=['POST'])
@login_required
def email_newsletter(newsletter_id):
    newsletter = db.get_or_404(Newsletter, newsletter_id)
    email_sent = send_newsletter_email(newsletter)
    if email_sent:
        flash("Your newsletter has been emailed to all subscribers!", "success")
    else:
        flash("Your newsletter was not emailed. Please check the subscriber list!", "danger")
    return redirect(url_for("newsletter_home"))


@app.route('/newsletter', methods=['GET', 'POST'])
@login_required
def newsletter_home():
    page = request.args.get('page', 1, type=int)
    newsletters = db.paginate(db.select(Newsletter).order_by(Newsletter.date_created.desc()), page=page, per_page=12)
    return render_template("newsletter_list.html", newsletters=newsletters, title="Newsletters Home")


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactUsForm()
    if form.validate_on_submit():
        msg = Message(
            subject=f"Contact Us Query from: {form.name.data}, email: {form.email.data}",
            sender="kagandajohn762@gmail.com",
            recipients=["kagandajohn762@gmail.com"],
            body=form.message.data
        )
        mail.send(msg)
        flash("Your query has been received! We will respond as soon as we can.", "success")
        return redirect(url_for("home"))
    return render_template("contact.html", form=form, title="Contact")


@app.route('/subscribe/list', methods=['GET', 'POST'])
@login_required
def subscriber_list():
    page = request.args.get('page', 1, type=int)
    subscribers = db.paginate(db.select(Subscriber).order_by(Subscriber.date_subscribed), page=page, per_page=12)
    return render_template("subscriber_list.html", subscribers=subscribers, title="Subscriber List")


@app.route('/subscribe/<int:subscriber_id>/delete', methods=['POST'])
@login_required
def delete_subscriber(subscriber_id):
    subscriber = db.get_or_404(Subscriber, subscriber_id)
    db.session.delete(subscriber)
    db.session.commit()
    flash("Subscriber has been deleted!", "success")
    return redirect(url_for("subscriber_list"))


@app.route('/user/list', methods=['GET', 'POST'])
@login_required
def user_list():
    page = request.args.get('page', 1, type=int)
    users = db.paginate(db.select(User).order_by(User.date_created), page=page, per_page=12)
    return render_template("user_list.html", users=users, title="User List")


@app.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    admin_delete = False
    if current_user.id != user_id:
        admin_delete = True

    user = db.get_or_404(User, user_id)
    delete_picture(user.profile_pic, "profile")
    if user.admin:
        for post in user.posts:
            delete_picture(post.profile_pic, "post")
    db.session.delete(user)
    db.session.commit()

    if admin_delete:
        flash("User has been deleted!", "success")
        return redirect(url_for("user_list"))
    else:
        logout_user()
        flash("Your account has been deleted!", "success")
        return redirect(url_for('home'))


@app.route('/user-details/<int:user_id>', methods=['GET', 'POST'])
@login_required
def user_details(user_id):
    user = db.get_or_404(User, user_id)
    image_file = url_for('static', filename=f'profile_pics/{user.profile_pic}')
    return render_template("user_details.html", user=user, image_file=image_file, title="User Details")


@app.route('/user-details/<int:user_id>/admin', methods=['POST'])
@login_required
def make_user_admin(user_id):
    user = db.get_or_404(User, user_id)
    user.admin = True
    db.session.commit()
    flash("User status has been updated to admin", "success")
    return redirect(url_for('user_details', user_id=user_id))


@app.route('/user-details/<int:user_id>/user', methods=['POST'])
@login_required
def make_admin_user(user_id):
    user = db.get_or_404(User, user_id)
    user.admin = False
    db.session.commit()
    flash("Admin status has been changed to user", "success")
    return redirect(url_for('user_details', user_id=user_id))

