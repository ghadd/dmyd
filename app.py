import os
import re
from operator import or_, and_

from flask import Flask, redirect, render_template, request, flash
from flask_login import current_user, login_required, login_user
from flask_socketio import SocketIO, join_room, emit
from werkzeug.datastructures import ImmutableMultiDict

from api import db, login_manager, Message, User
from utils import *

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/db.sqlite'
app.config['SECRET_KEY'] = os.urandom(24)

db.init_app(app)
login_manager.init_app(app)
socketio = SocketIO(app, manage_session=False)

# REMOVE IN PRODUCTION
with app.app_context():
    db.create_all(app=app)


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect('/chats')
    else:
        return render_template('index.html')


@app.route('/chats')
@login_required
def chats():
    friends = current_user.friends
    peer = get_active_chat_peer(current_user)

    # todo simplify by querying chat messages by connecting them to chats
    messages = Message.query.filter(
        or_(
            and_(Message.from_user == current_user,
                 Message.to_user == peer),
            and_(Message.from_user == peer,
                 Message.to_user == current_user)
        )
    )

    return render_template('chats.html', messages=messages, friends=friends)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = request.form
    if not form:
        return render_template('login.html')

    email = form['email']
    pwd = form['password']

    user = User.query.filter_by(email=email).first()
    if user:
        if user.matches_pwd(pwd):
            login_user(user)
            # clearing prev last chat
            user.current_chat_id = 0
            db.session.commit()
            return redirect('/chats')
        else:
            flash("Wrong password.")
    else:
        flash(f"User with email {email} not found.")
    return render_template('login.html', form=form)


@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    form = request.form
    if not form:
        return render_template('signup.html')

    name = form['name']
    surname = form['surname']
    email = form['email']
    pwd = form['password']
    pwd_rep = form['password_repeat']

    if pwd != pwd_rep:
        flash('Passwords don\'t match')
        return render_template('signup.html', form=form)

    user = User.query.filter_by(email=email).first()
    if user:
        flash(f'Email {email} is already in use.')
        form = ImmutableMultiDict()
        form['email'] = email
        return render_template('login.html', form=form)
    else:
        reg = r"[A-Za-z0-9_@.\[\]\<\>\~\!\@\#\&\+\-\%\^\(\)\|\/]{8,18}"
        match_re = re.compile(reg)

        if re.search(match_re, pwd):
            user = User(
                first_name=name,
                last_name=surname,
                email=email,
                password=pwd
            )
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect('/chats')
        else:
            flash("Password is weak.")
            return render_template('signup.html', form=form)


@app.route('/api/addFriend', methods=['POST'])
@login_required
def add_friend():
    friend_email = request.form['friend']
    friend = User.query.filter_by(email=friend_email).first()

    user = current_user
    user.friends.append(friend)
    db.session.commit()

    return redirect("/chats")


@socketio.on('join_chat')
def join_chat(arg):
    peer_id = arg['chat_id']

    chat = get_chat(current_user.id, peer_id)
    if not chat:
        chat = Chat(current_user, get_receiver(peer_id))
        db.session.add(chat)
        db.session.commit()

    join_room(str(chat.id))

    current_user.current_chat_id = chat.id
    db.session.commit()
    emit('enable_message_input')


@socketio.on('send_message')
def send_message(arg):
    msg = arg['message']
    ids = depair(current_user.current_chat_id)
    receiver_id = ids[0] if ids[0] != current_user.id else ids[1]

    message = Message(
        current_user,
        get_receiver(receiver_id),
        msg
    )

    db.session.add(message)
    db.session.commit()
    emit('update_message',
         {'message': msg},
         room=str(current_user.current_chat_id)
         )
