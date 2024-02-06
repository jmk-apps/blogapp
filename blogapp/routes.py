from blogapp import app, db
from flask import render_template, redirect, url_for, flash, request, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from blogapp.forms import RegistrationForm, LoginForm, UpdateAccountForm
from blogapp.models import User
from flask_login import login_user, logout_user, login_required, current_user
import os
import secrets
from PIL import Image, ImageOps

posts = [
    {
        "username": "James Dean",
        "title": "How can we sing about love?",
        "subtitle": "Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum.",
        "content": "lorem ipsum dolor sit amet, consectetur adipiscing elit sed do eiusmod tempor",
        "category": "Journey",
        "image_file": "static/img/articles/8.jpg",
        "date_posted": "26 october 2021"
    },
    {
        "username": "James Dean",
        "title": "Oh, I guess they have the blues",
        "subtitle": "Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. ",
        "content": "lorem ipsum dolor sit amet, consectetur adipiscing elit sed do eiusmod tempor",
        "category": "Lifestyle",
        "image_file": "static/img/articles/22.jpg",
        "date_posted": "3 october 2021"
    },
    {
        "username": "James Dean",
        "title": "How can we, how can we sing about ourselves?",
        "subtitle": "Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. ",
        "content": "lorem ipsum dolor sit amet, consectetur adipiscing elit sed do eiusmod tempor",
        "category": "Work",
        "image_file": "static/img/articles/19.jpg",
        "date_posted": "16 july 2021"
    },
    {
        "username": "James Dean",
        "title": "The king is made of paper",
        "subtitle": "Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. ",
        "content": "lorem ipsum dolor sit amet, consectetur adipiscing elit sed do eiusmod tempor",
        "category": "Lifestyle",
        "image_file": "static/img/articles/3.jpg",
        "date_posted": "15 october 2021"
    },
]


@app.route('/')
def home():
    return render_template("index.html", posts=posts)


@app.route('/about')
def about():
    return render_template("about.html", title="About")


def save_picture(form_picture):
    # Get the filename and path
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    # Resize and save the picture
    output_size = (250, 250)
    with Image.open(form_picture) as img:
        ImageOps.cover(img, output_size).save(picture_path)

    return picture_fn


def delete_picture(picture_name):
    if picture_name != "default_profile_pic.jpg":
        picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_name)
        os.remove(picture_path)


@app.route('/account', methods=["GET", "POST"])
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.profile_pic.data:
            delete_picture(current_user.profile_pic)
            picture_file = save_picture(form.profile_pic.data)
            current_user.profile_pic = picture_file
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


@app.route('/contact')
def contact():
    return render_template("contact.html", title="Contact")
