from typing import Optional

from ArchRobot.db.mongo import db

USERS = db.users


def lang(user_id: int) -> Optional[str]:
    """Get the language preference for a user.

    Args:
        user_id: The Telegram user ID.

    Returns:
        The language code (e.g., 'en', 'es', 'ru') or None if not set.
    """
    data = USERS.find_one({"_id": user_id}, {"lang": 1})
    return data.get("lang") if data else None


def set_lang(user_id: int, lang_code: str) -> None:
    """Set the language preference for a user.

    Args:
        user_id: The Telegram user ID.
        lang_code: The language code to set.
    """
    USERS.update_one(
        {"_id": user_id},
        {"$set": {"lang": lang_code}},
        upsert=True,
    )


async def update_user(user_id: int, username: Optional[str] = None, lang_code: Optional[str] = None) -> None:
    """Update user information in the database.

    Args:
        user_id: The Telegram user ID.
        username: The user's username (optional).
        lang_code: The language code (optional).
    """
    update = {}
    if username is not None:
        update["username"] = username
    if lang_code is not None:
        update["lang"] = lang_code
    if update:
        USERS.update_one(
            {"_id": user_id},
            {"$set": update},
            upsert=True,
        )


def agreed(user_id: int) -> bool:
    """Check if a user has agreed to the privacy policy.

    Args:
        user_id: The Telegram user ID.

    Returns:
        True if the user has agreed, False otherwise.
    """
    data = USERS.find_one({"_id": user_id}, {"agreed": 1})
    return bool(data and data.get("agreed", False))


def set_agreed(user_id: int) -> None:
    """Mark that a user has agreed to the privacy policy.

    Args:
        user_id: The Telegram user ID.
    """
    USERS.update_one(
        {"_id": user_id},
        {"$set": {"agreed": True}},
        upsert=True,
    )