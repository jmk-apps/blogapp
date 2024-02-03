from blogapp import app
from flask import render_template
from blogapp.forms import RegistrationForm

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


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        print("Registration Successful")
    return render_template("register.html", form=form, title="Register")


@app.route('/contact')
def contact():
    return render_template("contact.html", title="Contact")
