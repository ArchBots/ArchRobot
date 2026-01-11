from datetime import datetime
from ArchRobot.db.mongo import db, adb


_u = db.users
_u_async = adb.users


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


async def update_user(user_id: int, username: str = None, language: str = None):
    update_data = {
        "user_id": user_id,
    }
    
    if username:
        update_data["username"] = username
    
    if language:
        update_data["language"] = language
    
    await _u_async.update_one(
        {"_id": user_id},
        {
            "$set": update_data,
            "$setOnInsert": {"first_seen": datetime.utcnow()}
        },
        upsert=True
    )