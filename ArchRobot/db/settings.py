from ArchRobot.db.mongo import db


_s = db.settings


def get(cid: int, k: str, d=None):
    x = _s.find_one({"_id": cid}, {k: 1})
    return x.get(k, d) if x else d


def set(cid: int, k: str, v):
    _s.update_one({"_id": cid}, {"$set": {k: v}}, upsert=True)


def anon(cid: int) -> bool:
    return bool(get(cid, "anonadmin", False))


def err(cid: int) -> bool:
    return bool(get(cid, "adminerror", True))


def set_anon(cid: int, v: bool):
    set(cid, "anonadmin", v)


def set_err(cid: int, v: bool):
    set(cid, "adminerror", v)