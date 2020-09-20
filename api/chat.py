import json

from pairing import pair

from crypto import *
from .user import User
from .api import db


class Chat(db.Model):
    __tablename__ = 'chats'

    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    user1_id = db.Column(db.ForeignKey(User.id))
    user1 = db.relationship('User', backref='user1', lazy=True, uselist=False, foreign_keys=[user1_id])

    user2_id = db.Column(db.ForeignKey(User.id))
    user2 = db.relationship('User', backref='user2', lazy=True, uselist=False, foreign_keys=[user2_id])

    contents = db.Column(db.String)

    def __init__(self, user1, user2):
        self.id = pair(user1.id, user2.id)
        self.user1 = user1
        self.user2 = user2

    def __repr__(self):
        return '<Chat %r>' % self.id
