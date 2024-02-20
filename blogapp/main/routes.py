from flask import render_template, Blueprint, request, redirect, url_for, flash
from blogapp import db
from blogapp.models import Post, User
from blogapp import mail
from blogapp.main.forms import SearchForm, ContactUsForm
from flask_mail import Message
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

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
def home():
    page = request.args.get('page', 1, type=int)
    posts = db.paginate(db.select(Post).order_by(Post.date_posted.desc()), page=page, per_page=3)
    return render_template("index.html", posts=posts)


@main.route('/about')
def about():
    return render_template("about.html", title="About")


@main.route('/contact', methods=['GET', 'POST'])
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
        return redirect(url_for("main.home"))
    return render_template("contact.html", form=form, title="Contact")


@main.route('/search', methods=['GET', 'POST'])
def search():
    stmt = db.select(Post).order_by(Post.date_posted.desc())
    page = request.args.get('page', 1, type=int)
    param = request.args.get("param")
    username = request.args.get("username")

    search_value = request.form.get("search")
    if search_value:
        stmt = db.select(Post).where(Post.content.icontains(search_value)).order_by(Post.date_posted.desc())
    elif param in categories:
        stmt = db.select(Post).filter_by(category=param).order_by(Post.date_posted.desc())
    elif param in archives:
        stmt = db.select(Post).where(Post.date_posted.icontains(param)).order_by(Post.date_posted.desc())
    elif param:
        stmt = db.select(Post).where(Post.author_username == param).order_by(Post.date_posted.desc())

    posts = db.paginate(stmt, page=page, per_page=3)
    return render_template("search.html", param_value=param, search_value=search_value, posts=posts, title="Search")
