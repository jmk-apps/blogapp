from blogapp import app, db
from flask import render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from blogapp.forms import RegistrationForm, LoginForm, UpdateAccountForm
from blogapp.models import User
from flask_login import login_user, logout_user, login_required

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


@app.route('/account', methods=["GET", "POST"])
def account():
    form = UpdateAccountForm()
    return render_template("account.html", form=form, title="Account")


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
