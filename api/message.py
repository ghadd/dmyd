import json

from crypto import *
from .user import User
from .api import db


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    from_user_id = db.Column(db.ForeignKey(User.id))
    from_user = db.relationship('User', backref='sender_message', lazy=True, uselist=False, foreign_keys=[from_user_id])

    to_user_id = db.Column(db.ForeignKey(User.id))
    to_user = db.relationship('User', backref='receiver_message', lazy=True, uselist=False, foreign_keys=[to_user_id])

    contents = db.Column(db.String)

    def __init__(self, from_user, to_user, contents):
        self.from_user = from_user
        self.to_user = to_user
        self.contents = json.dumps(encrypt(contents, str(from_user.tpass) + str(to_user.tpass)))

    def __repr__(self):
        return '<Message %r>' % self.id
