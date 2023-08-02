import threading

from sqlalchemy import Column, String

from ArchRobot.modules.sql import BASE, SESSION


class ArchBotsChats(BASE):
    __tablename__ = "archbots_chats"
    chat_id = Column(String(14), primary_key=True)

    def __init__(self, chat_id):
        self.chat_id = chat_id


ArchBotsChats.__table__.create(checkfirst=True)
INSERTION_LOCK = threading.RLock()


def is_archbots(chat_id):
    try:
        chat = SESSION.query(ArchBotsChats).get(str(chat_id))
        return bool(chat)
    finally:
        SESSION.close()


def set_archbots(chat_id):
    with INSERTION_LOCK:
        archbotschat = SESSION.query(ArchBotsChats).get(str(chat_id))
        if not archbotschat:
            archbotschat = ArchBotsChats(str(chat_id))
        SESSION.add(archbotschat)
        SESSION.commit()


def rem_archbots(chat_id):
    with INSERTION_LOCK:
        mukeshchat = SESSION.query(MukeshChats).get(str(chat_id))
        if mukeshchat:
            SESSION.delete(archbotschat)
        SESSION.commit()
