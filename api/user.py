import hashlib

from flask_login import UserMixin

from .api import db, login_manager

friends_table = db.Table('friends',
                         db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
                         db.Column('friend_id', db.Integer, db.ForeignKey('users.id'))
                         )


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String, nullable=True)
    email = db.Column(db.Integer, unique=True)
    pwd_hash = db.Column(db.Integer)
    tpass = db.Column(db.Integer)
    current_chat_id = db.Column(db.Integer, default=0)

    friends = db.relationship('User',  # defining the relationship, User is left side entity
                              secondary=friends_table,
                              primaryjoin=(friends_table.c.user_id == id),
                              secondaryjoin=(friends_table.c.friend_id == id),
                              lazy='dynamic'
                              )

    def matches_pwd(self, pwd):
        return self.pwd_hash == hashlib.md5(pwd.encode()).hexdigest()

    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.pwd_hash = hashlib.md5(password.encode()).hexdigest()
        self.tpass = hashlib.md5(email.encode()).hexdigest()

    def __repr__(self):
        return '<User %r>' % self.id


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
