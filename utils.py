import json
from operator import or_

from pairing import *

from api import User
from api import Chat
from crypto import decrypt


def get_receiver(uid):
    if not uid:
        return None

    return User.query.filter_by(id=uid).first()


def decrypt_message(message):
    message_enc = json.loads(message.contents)
    pwd = str(message.from_user.tpass) + str(message.to_user.tpass)

    return decrypt(message_enc, pwd)


def get_chat(uid1, uid2):
    res1 = Chat.query.get(
        pair(uid1, uid2)
    )

    res2 = Chat.query.get(
        pair(uid2, uid1)
    )

    return res1 or res2


def get_chat_peer(user):
    chat = Chat.query.filter(or_(Chat.user1 == user, Chat.user2 == user)).first()
    if not chat:
        return None

    return chat.user2 if chat.user1 == user else chat.user1


def get_active_chat_peer(user):
    chat = Chat.query.filter(or_(Chat.user1 == user, Chat.user2 == user)).first()
    if (not chat) or (chat.id != user.current_chat_id):
        return None

    return chat.user2 if chat.user1 == user else chat.user1
