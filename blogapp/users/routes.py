from flask import Blueprint, flash, render_template, redirect, url_for, request
from blogapp import db
from flask_login import login_required, current_user, login_user, logout_user
from blogapp.models import User, Subscriber
from blogapp.users.forms import LoginForm, RegistrationForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from blogapp.users.utils import (delete_picture, save_picture, send_subscriber_email, send_reset_email,
                                 validate_subscriber_email, verify_subscribe_token, admin_required)

users = Blueprint('users', __name__)


@users.route('/account', methods=["GET", "POST"])
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
        return redirect(url_for('users.account'))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    profile_picture = url_for('static', filename=f'profile_pics/{current_user.profile_pic}')
    return render_template("account.html", form=form, image_file=profile_picture, title="Account")


@users.route('/register', methods=['GET', 'POST'])
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
        return redirect(url_for('users.login'))
    return render_template("register.html", form=form, title="Register")


@users.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.execute(db.select(User).where(User.email == form.email.data)).scalar()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template("login.html", form=form, title="Login")


@users.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    form = RequestResetForm()
    if form.validate_on_submit():
        user = db.session.execute(db.select(User).where(User.email == form.email.data)).scalar()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password', 'primary')
        return redirect(url_for('users.login'))
    return render_template("reset_request.html", form=form, title="Reset Password")


@users.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token.', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template("reset_token.html", form=form, title="Reset Password")


@users.route('/subscribe', methods=['GET', 'POST'])
def subscribe_request():
    email = request.form.get('email')
    if validate_subscriber_email(email):
        subscriber = db.session.execute(db.select(Subscriber).where(Subscriber.email == email)).scalar()
        if subscriber:
            flash('That email is already included in the subscriber list.', 'success')
            return redirect(url_for('main.home'))
        send_subscriber_email(email)
        flash('An email has been sent with instructions to subscribe to the monthly newsletter', 'primary')
        return redirect(url_for('main.home'))
    else:
        flash('The email entered was invalid, please enter a valid email', 'danger')
        return redirect(url_for('main.home'))


@users.route('/subscribe/<token>', methods=['GET', 'POST'])
def subscribe_token(token):
    subscriber_email = verify_subscribe_token(token)
    current_subscriber_email = db.session.execute(
        db.select(Subscriber).where(Subscriber.email == subscriber_email)).scalar()
    if subscriber_email is None or current_subscriber_email:
        flash('That is an invalid or expired token.', 'warning')
        return redirect(url_for('main.home'))
    new_subscriber = Subscriber(
        email=subscriber_email,
        date_subscribed=datetime.now(timezone.utc)
    )
    db.session.add(new_subscriber)
    db.session.commit()
    flash('Your have successfully subscribed to our monthly newsletter', 'success')
    return redirect(url_for('main.home'))


@users.route('/subscribe/list', methods=['GET', 'POST'])
@admin_required
@login_required
def subscriber_list():
    page = request.args.get('page', 1, type=int)
    subscribers = db.paginate(db.select(Subscriber).order_by(Subscriber.date_subscribed), page=page, per_page=12)
    return render_template("subscriber_list.html", subscribers=subscribers, title="Subscriber List")


@users.route('/subscribe/<int:subscriber_id>/delete', methods=['POST'])
@admin_required
@login_required
def delete_subscriber(subscriber_id):
    subscriber = db.get_or_404(Subscriber, subscriber_id)
    db.session.delete(subscriber)
    db.session.commit()
    flash("Subscriber has been deleted!", "success")
    return redirect(url_for("users.subscriber_list"))


@users.route('/user/list', methods=['GET', 'POST'])
@admin_required
@login_required
def user_list():
    page = request.args.get('page', 1, type=int)
    users = db.paginate(db.select(User).order_by(User.date_created), page=page, per_page=12)
    return render_template("user_list.html", users=users, title="User List")


@users.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    admin_delete = False
    if current_user.id != user_id:
        admin_delete = True

    user = db.get_or_404(User, user_id)
    delete_picture(user.profile_pic, "profile")

    for post in user.posts:
        delete_picture(post.post_pic, "post")

    db.session.delete(user)
    db.session.commit()

    if admin_delete:
        flash("User has been deleted!", "success")
        return redirect(url_for("users.user_list"))
    else:
        logout_user()
        flash("Your account has been deleted!", "success")
        return redirect(url_for('main.home'))


@users.route('/user-details/<int:user_id>', methods=['GET', 'POST'])
@admin_required
@login_required
def user_details(user_id):
    user = db.get_or_404(User, user_id)
    image_file = url_for('static', filename=f'profile_pics/{user.profile_pic}')
    return render_template("user_details.html", user=user, image_file=image_file, title="User Details")


@users.route('/user-details/<int:user_id>/admin', methods=['POST'])
@admin_required
@login_required
def make_user_admin(user_id):
    user = db.get_or_404(User, user_id)
    user.admin = True
    db.session.commit()
    flash("User status has been updated to admin", "success")
    return redirect(url_for('users.user_details', user_id=user_id))


@users.route('/user-details/<int:user_id>/user', methods=['POST'])
@admin_required
@login_required
def make_admin_user(user_id):
    user = db.get_or_404(User, user_id)
    user.admin = False
    db.session.commit()
    flash("Admin status has been changed to user", "success")
    return redirect(url_for('users.user_details', user_id=user_id))
