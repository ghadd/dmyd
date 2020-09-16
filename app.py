import re

from flask import Flask, render_template, request
from pathlib import Path

from api.models import db
from api.models.user import User

Path("./database").mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/db.sqlite'
db.init_app(app)

with app.app_context():
    db.create_all(app=app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login/')
def login():
    return render_template('login.html')


@app.route('/signup/')
def signup():
    return render_template('signup.html')


@app.route('/api/login', methods=['POST'])
def api_login():
    form = request.form
    email = form['email']
    pwd = form['password']

    user = User.query.filter_by(email=email).first()
    if user:
        if user.matches_pwd(pwd):
            return 'Logged'
        else:
            return 'Wrong pass'
    else:
        return 'No such user'


@app.route('/api/signup', methods=['POST'])
def api_signup():
    form = request.form
    name = form['name']
    surname = form['surname']
    email = form['email']
    pwd = form['password']
    pwd_rep = form['password_repeat']

    if pwd != pwd_rep:
        return 'Passwords dont match'

    user = User.query.filter_by(email=email).first()
    if user:
        return 'Already registered'
    else:
        reg = r"[A-Za-z0-9_@.\[\]\<\>\~\!\@\#\&\+\-\%\^\(\)\|\/]{8,18}"
        match_re = re.compile(reg)

        if re.search(match_re, pwd):
            db.session.add(
                User(
                    first_name=name,
                    last_name=surname,
                    email=email,
                    password=pwd
                )
            )
            db.session.commit()
            return 'Cool!'
        else:
            return 'Bad pass'
