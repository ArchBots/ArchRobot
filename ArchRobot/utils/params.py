from enum import Enum
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import ChatMember


class PermissionLevel(Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    BOT_ADMIN = "bot_admin"


def get_permission_level(member: ChatMember) -> PermissionLevel:
    if member.status == ChatMemberStatus.OWNER:
        return PermissionLevel.OWNER
    elif member.status == ChatMemberStatus.ADMINISTRATOR:
        return PermissionLevel.ADMIN
    else:
        return PermissionLevel.MEMBER


async def check_permission(client, chat_id: int, user_id: int, required: PermissionLevel) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        user_level = get_permission_level(member)

        if required == PermissionLevel.OWNER:
            return user_level == PermissionLevel.OWNER
        elif required == PermissionLevel.ADMIN:
            return user_level in (PermissionLevel.OWNER, PermissionLevel.ADMIN)
        elif required == PermissionLevel.MEMBER:
            return True

        return False
    except Exception:
        return False


async def is_bot_admin(client, chat_id: int, bot_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, bot_id)
        return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
    except Exception:
        return False


async def bot_can_delete(client, chat_id: int, bot_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, bot_id)
        if member.status != ChatMemberStatus.ADMINISTRATOR:
            return False
        return member.privileges and member.privileges.can_delete_messages
    except Exception:
        return False


async def bot_can_restrict(client, chat_id: int, bot_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, bot_id)
        if member.status != ChatMemberStatus.ADMINISTRATOR:
            return False
        return member.privileges and member.privileges.can_restrict_members
    except Exception:
        return False