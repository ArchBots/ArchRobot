from ArchRobot.db import db

ANTIBIO = db.antibio


def get(chat_id: int) -> bool:
    data = ANTIBIO.find_one({"chat_id": chat_id})
    return bool(data and data.get("enabled", False))


def enable(chat_id: int) -> bool:
    if get(chat_id):
        return False
    ANTIBIO.update_one(
        {"chat_id": chat_id},
        {"$set": {"enabled": True}},
        upsert=True
    )
    return True


def disable(chat_id: int) -> bool:
    if not get(chat_id):
        return False
    ANTIBIO.update_one(
        {"chat_id": chat_id},
        {"$set": {"enabled": False}},
        upsert=True
    )
    return True