from ArchRobot.db.mongo import db

USERS = db.users


def lang(user_id: int) -> str:
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