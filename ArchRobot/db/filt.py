from datetime import datetime
from typing import Optional, List, Dict, Any
import hashlib

from ArchRobot.db.mongo import adb


_filters = adb.filters
_filter_replies = adb.filter_replies


async def create_indexes():
    await _filters.create_index("chat_id")
    await _filters.create_index("trigger_hash")
    await _filters.create_index([("chat_id", 1), ("trigger_hash", 1)], unique=True)
    await _filter_replies.create_index("reply_id", unique=True)
    await _filter_replies.create_index("content_hash")
    await _filter_replies.create_index("file_unique_id")


def normalize_trigger(trigger: str) -> str:
    return trigger.strip().lower()


def hash_trigger(normalized: str) -> str:
    return hashlib.sha256(normalized.encode()).hexdigest()


def hash_content(content: str) -> str:
    if not content:
        content = ""
    return hashlib.sha256(content.encode()).hexdigest()


async def find_or_create_reply(
    reply_type: str,
    content: Optional[str] = None,
    file_id: Optional[str] = None,
    file_unique_id: Optional[str] = None
) -> str:
    content_hash = hash_content(content) if content else None
    
    if content_hash:
        existing = await _filter_replies.find_one({"content_hash": content_hash})
        if existing:
            return existing["reply_id"]
    
    if file_unique_id:
        existing = await _filter_replies.find_one({"file_unique_id": file_unique_id})
        if existing:
            return existing["reply_id"]
    
    reply_id = hashlib.sha256(
        f"{reply_type}{content or ''}{file_id or ''}{datetime.utcnow().isoformat()}".encode()
    ).hexdigest()
    
    await _filter_replies.insert_one({
        "reply_id": reply_id,
        "reply_type": reply_type,
        "content": content,
        "file_id": file_id,
        "file_unique_id": file_unique_id,
        "content_hash": content_hash,
        "created_at": datetime.utcnow()
    })
    
    return reply_id


async def create_filter(
    chat_id: int,
    trigger_raw: str,
    trigger_norm: str,
    flags: List[str],
    reply_id: str,
    created_by: int
) -> bool:
    trigger_hash = hash_trigger(trigger_norm)
    
    try:
        await _filters.insert_one({
            "chat_id": chat_id,
            "trigger_raw": trigger_raw,
            "trigger_norm": trigger_norm,
            "trigger_hash": trigger_hash,
            "flags": flags,
            "reply_id": reply_id,
            "created_by": created_by,
            "created_at": datetime.utcnow()
        })
        return True
    except Exception:
        return False


async def get_filter(chat_id: int, trigger_norm: str) -> Optional[Dict[str, Any]]:
    trigger_hash = hash_trigger(trigger_norm)
    return await _filters.find_one({"chat_id": chat_id, "trigger_hash": trigger_hash})


async def get_chat_filters(chat_id: int) -> List[Dict[str, Any]]:
    cursor = _filters.find({"chat_id": chat_id})
    return await cursor.to_list(length=None)


async def delete_filter(chat_id: int, trigger_norm: str) -> bool:
    trigger_hash = hash_trigger(trigger_norm)
    result = await _filters.delete_one({"chat_id": chat_id, "trigger_hash": trigger_hash})
    return result.deleted_count > 0


async def delete_all_filters(chat_id: int) -> int:
    result = await _filters.delete_many({"chat_id": chat_id})
    return result.deleted_count


async def get_reply(reply_id: str) -> Optional[Dict[str, Any]]:
    return await _filter_replies.find_one({"reply_id": reply_id})


async def find_matching_filter(chat_id: int, text: str) -> Optional[Dict[str, Any]]:
    filters = await get_chat_filters(chat_id)
    
    text_lower = text.lower()
    words = text_lower.split()
    
    for f in filters:
        flags = f.get("flags", [])
        trigger_norm = f["trigger_norm"]
        
        if "exact" in flags:
            if text_lower == trigger_norm:
                return f
        elif "prefix" in flags:
            if text_lower.startswith(trigger_norm):
                return f
        else:
            if trigger_norm in words or trigger_norm in text_lower:
                return f
    
    return None