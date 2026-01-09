from ArchRobot.db.mongo import db


_u = db.users


def lang(uid: int):
    d = _u.find_one({"_id": uid}, {"lang": 1})
    return d.get("lang") if d else None


def set_lang(uid: int, v: str):
    _u.update_one({"_id": uid}, {"$set": {"lang": v}}, upsert=True)


def agreed(uid: int) -> bool:
    d = _u.find_one({"_id": uid}, {"agree": 1})
    return bool(d and d.get("agree"))


def set_agreed(uid: int):
    _u.update_one({"_id": uid}, {"$set": {"agree": True}}, upsert=True)