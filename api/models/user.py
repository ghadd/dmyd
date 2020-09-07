import hashlib

from . import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String, nullable=True)
    email = db.Column(db.Integer, unique=True)
    pwd_hash = db.Column(db.Integer)

    # todo peers

    def matches_pwd(self, pwd):
        return self.pwd_hash == hashlib.md5(pwd.encode()).hexdigest()

    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.pwd_hash = hashlib.md5(password.encode()).hexdigest()

    def __repr__(self):
        return '<User %r>' % self.id
