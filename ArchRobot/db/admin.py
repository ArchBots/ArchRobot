from ArchRobot.db.mongo import adb

col = adb.admin_promotions


async def set_promoter(chat_id: int, user_id: int, promoter_id: int):
    await col.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$set": {"promoter_id": promoter_id}},
        upsert=True,
    )


async def get_promoter(chat_id: int, user_id: int):
    x = await col.find_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"_id": 0, "promoter_id": 1},
    )
    return x["promoter_id"] if x else None


async def clear_promoter(chat_id: int, user_id: int):
    await col.delete_one({"chat_id": chat_id, "user_id": user_id})>