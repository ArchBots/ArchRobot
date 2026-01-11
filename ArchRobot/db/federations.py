from datetime import datetime
from typing import Optional, List, Dict, Any

from ArchRobot.db.mongo import adb


_federations = adb.federations
_federation_chats = adb.federation_chats
_federation_bans = adb.federation_bans


async def create_indexes():
    await _federations.create_index("federation_id", unique=True)
    await _federations.create_index("owner_id")
    await _federation_chats.create_index("federation_id")
    await _federation_chats.create_index("chat_id")
    await _federation_chats.create_index([("federation_id", 1), ("chat_id", 1)], unique=True)
    await _federation_bans.create_index("federation_id")
    await _federation_bans.create_index("user_id")
    await _federation_bans.create_index([("federation_id", 1), ("user_id", 1)], unique=True)


async def create_federation(federation_id: str, name: str, owner_id: int) -> bool:
    try:
        await _federations.insert_one({
            "federation_id": federation_id,
            "name": name,
            "owner_id": owner_id,
            "admin_ids": [],
            "created_at": datetime.utcnow(),
        })
        return True
    except Exception:
        return False


async def get_federation(federation_id: str) -> Optional[Dict[str, Any]]:
    return await _federations.find_one({"federation_id": federation_id})


async def rename_federation(federation_id: str, new_name: str) -> bool:
    result = await _federations.update_one(
        {"federation_id": federation_id},
        {"$set": {"name": new_name}}
    )
    return result.modified_count > 0


async def delete_federation(federation_id: str) -> bool:
    await _federation_chats.delete_many({"federation_id": federation_id})
    await _federation_bans.delete_many({"federation_id": federation_id})
    result = await _federations.delete_one({"federation_id": federation_id})
    return result.deleted_count > 0


async def get_user_federations(user_id: int) -> List[Dict[str, Any]]:
    cursor = _federations.find({
        "$or": [
            {"owner_id": user_id},
            {"admin_ids": user_id}
        ]
    })
    return await cursor.to_list(length=None)


async def is_fed_admin(federation_id: str, user_id: int) -> bool:
    fed = await _federations.find_one({"federation_id": federation_id})
    if not fed:
        return False
    return fed["owner_id"] == user_id or user_id in fed.get("admin_ids", [])


async def is_fed_owner(federation_id: str, user_id: int) -> bool:
    fed = await _federations.find_one({"federation_id": federation_id})
    if not fed:
        return False
    return fed["owner_id"] == user_id


async def add_fed_admin(federation_id: str, user_id: int) -> bool:
    result = await _federations.update_one(
        {"federation_id": federation_id},
        {"$addToSet": {"admin_ids": user_id}}
    )
    return result.modified_count > 0


async def remove_fed_admin(federation_id: str, user_id: int) -> bool:
    result = await _federations.update_one(
        {"federation_id": federation_id},
        {"$pull": {"admin_ids": user_id}}
    )
    return result.modified_count > 0


async def get_fed_admins(federation_id: str) -> List[int]:
    fed = await _federations.find_one({"federation_id": federation_id})
    if not fed:
        return []
    return fed.get("admin_ids", [])


async def link_chat(federation_id: str, chat_id: int, linked_by: int) -> bool:
    try:
        await _federation_chats.insert_one({
            "federation_id": federation_id,
            "chat_id": chat_id,
            "linked_by": linked_by,
            "linked_at": datetime.utcnow(),
        })
        return True
    except Exception:
        return False


async def unlink_chat(chat_id: int) -> bool:
    result = await _federation_chats.delete_one({"chat_id": chat_id})
    return result.deleted_count > 0


async def get_chat_federation(chat_id: int) -> Optional[str]:
    doc = await _federation_chats.find_one({"chat_id": chat_id})
    return doc["federation_id"] if doc else None


async def get_fed_chats(federation_id: str) -> List[int]:
    cursor = _federation_chats.find({"federation_id": federation_id})
    docs = await cursor.to_list(length=None)
    return [doc["chat_id"] for doc in docs]


async def fed_ban_user(federation_id: str, user_id: int, reason_key: str, banned_by: int) -> bool:
    try:
        await _federation_bans.insert_one({
            "federation_id": federation_id,
            "user_id": user_id,
            "reason_key": reason_key,
            "banned_by": banned_by,
            "banned_at": datetime.utcnow(),
        })
        return True
    except Exception:
        await _federation_bans.update_one(
            {"federation_id": federation_id, "user_id": user_id},
            {"$set": {
                "reason_key": reason_key,
                "banned_by": banned_by,
                "banned_at": datetime.utcnow(),
            }}
        )
        return True


async def fed_unban_user(federation_id: str, user_id: int) -> bool:
    result = await _federation_bans.delete_one({
        "federation_id": federation_id,
        "user_id": user_id
    })
    return result.deleted_count > 0


async def is_fed_banned(federation_id: str, user_id: int) -> bool:
    doc = await _federation_bans.find_one({
        "federation_id": federation_id,
        "user_id": user_id
    })
    return doc is not None


async def get_fed_bans(federation_id: str) -> List[Dict[str, Any]]:
    cursor = _federation_bans.find({"federation_id": federation_id})
    return await cursor.to_list(length=None)


async def get_user_fed_bans(user_id: int) -> List[Dict[str, Any]]:
    cursor = _federation_bans.find({"user_id": user_id})
    return await cursor.to_list(length=None)
