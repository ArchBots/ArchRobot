import time
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus, MessageEntityType, ChatType
from pyrogram.types import ChatAdministratorRights

from ArchRobot import arch
from strings import get_string
from ArchRobot.db.users import lang, update_user
from ArchRobot.db.admin import set_promoter, get_promoter, clear_promoter


__mod_name__ = "Admin"
__help__ = "AHELP"


_cache = {}
_CACHE_TTL = 300


def _cache_key(chat_id, user_id):
    return (chat_id, user_id)


def _get_cached(chat_id, user_id):
    key = _cache_key(chat_id, user_id)
    if key in _cache:
        val, ts = _cache[key]
        if time.time() - ts < _CACHE_TTL:
            return val
        del _cache[key]
    return None


def _set_cached(chat_id, user_id, val):
    _cache[_cache_key(chat_id, user_id)] = (val, time.time())


def _invalidate_cache(chat_id, user_id):
    key = _cache_key(chat_id, user_id)
    if key in _cache:
        del _cache[key]


def _s(uid):
    return get_string(lang(uid) or "en")


async def _get_member(c, chat_id, user_id):
    cached = _get_cached(chat_id, user_id)
    if cached is not None:
        return cached
    member = await c.get_chat_member(chat_id, user_id)
    _set_cached(chat_id, user_id, member)
    return member


async def _target(c, m):
    if m.reply_to_message:
        return m.reply_to_message.from_user
    if m.entities:
        for e in m.entities:
            if e.type == MessageEntityType.TEXT_MENTION and e.user:
                return e.user
    if len(m.command) < 2:
        return None
    try:
        return await c.get_users(m.command[1])
    except Exception:
        return None


def _mix(bot, user):
    rights = ChatAdministratorRights(
        can_manage_chat=bot.can_manage_chat and user.can_manage_chat,
        can_change_info=bot.can_change_info and user.can_change_info,
        can_delete_messages=bot.can_delete_messages and user.can_delete_messages,
        can_manage_video_chats=bot.can_manage_video_chats and user.can_manage_video_chats,
        can_restrict_members=bot.can_restrict_members and user.can_restrict_members,
        can_invite_users=bot.can_invite_users and user.can_invite_users,
        can_pin_messages=bot.can_pin_messages and user.can_pin_messages,
        can_manage_topics=bot.can_manage_topics and user.can_manage_topics,
        can_post_messages=bot.can_post_messages and user.can_post_messages,
        can_edit_messages=bot.can_edit_messages and user.can_edit_messages,
        can_post_stories=bot.can_post_stories and user.can_post_stories,
        can_edit_stories=bot.can_edit_stories and user.can_edit_stories,
        can_delete_stories=bot.can_delete_stories and user.can_delete_stories,
    )
    if not any(vars(rights).values()):
        rights.can_delete_messages = True
    return rights


def _demote():
    return ChatAdministratorRights(
        can_manage_chat=False,
        can_change_info=False,
        can_delete_messages=False,
        can_manage_video_chats=False,
        can_restrict_members=False,
        can_invite_users=False,
        can_pin_messages=False,
        can_manage_topics=False,
        can_post_messages=False,
        can_edit_messages=False,
        can_post_stories=False,
        can_edit_stories=False,
        can_delete_stories=False,
    )


@arch.on_message(filters.command(["promote"], prefixes=["/", "!", "."]), group=1)
async def promote(c, m):
    if m.chat.type == ChatType.PRIVATE:
        s = _s(m.from_user.id)
        return await m.reply_text(s["GROUP_ONLY"])
    s = _s(m.from_user.id)
    await update_user(m.from_user.id, m.from_user.username)
    bot = await _get_member(c, m.chat.id, arch.me.id)
    if not bot.privileges or not bot.privileges.can_promote_members:
        return await m.reply_text(s["ABOTP"])
    provider = await _get_member(c, m.chat.id, m.from_user.id)
    if provider.status != ChatMemberStatus.OWNER:
        if not provider.privileges or not provider.privileges.can_promote_members:
            return await m.reply_text(s["AUSERP"])
    u = await _target(c, m)
    if not u:
        return await m.reply_text(s["ATARGET"])
    await update_user(u.id, u.username)
    target = await _get_member(c, m.chat.id, u.id)
    if target.status == ChatMemberStatus.OWNER:
        return await m.reply_text(s["AOWNER"])
    if target.status == ChatMemberStatus.ADMINISTRATOR:
        return await m.reply_text(s["AALREADY"])
    explicit_title = " ".join(m.command[2:]) if len(m.command) > 2 else None
    try:
        if provider.status == ChatMemberStatus.OWNER:
            rights = bot.privileges
        else:
            rights = _mix(bot.privileges, provider.privileges)
        await c.promote_chat_member(
            m.chat.id,
            u.id,
            privileges=rights,
        )
        title = explicit_title or (u.username.lstrip("@") if u.username else None) or u.first_name or "Admin"
        try:
            await c.set_administrator_title(m.chat.id, u.id, title[:16])
        except Exception:
            pass
        await set_promoter(m.chat.id, u.id, m.from_user.id)
        _invalidate_cache(m.chat.id, u.id)
        return await m.reply_text(s["APOK"])
    except Exception:
        return await m.reply_text(s["APFAIL"])


@arch.on_message(filters.command(["demote"], prefixes=["/", "!", "."]), group=1)
async def demote(c, m):
    if m.chat.type == ChatType.PRIVATE:
        s = _s(m.from_user.id)
        return await m.reply_text(s["GROUP_ONLY"])
    s = _s(m.from_user.id)
    await update_user(m.from_user.id, m.from_user.username)
    bot = await _get_member(c, m.chat.id, arch.me.id)
    if not bot.privileges or not bot.privileges.can_promote_members:
        return await m.reply_text(s["ABOTP"])
    provider = await _get_member(c, m.chat.id, m.from_user.id)
    if provider.status != ChatMemberStatus.OWNER:
        if not provider.privileges or not provider.privileges.can_promote_members:
            return await m.reply_text(s["AUSERP"])
    u = await _target(c, m)
    if not u:
        return await m.reply_text(s["ATARGET"])
    target = await _get_member(c, m.chat.id, u.id)
    if target.status == ChatMemberStatus.OWNER:
        return await m.reply_text(s["AOWNER"])
    if target.status != ChatMemberStatus.ADMINISTRATOR:
        return await m.reply_text(s["ADFAIL"])
    promoter_id = await get_promoter(m.chat.id, u.id)
    if provider.status != ChatMemberStatus.OWNER:
        if promoter_id is None:
            return await m.reply_text(s["ANOTVIAME"])
        if promoter_id != m.from_user.id:
            return await m.reply_text(s["ANOTPROMOTED"])
    try:
        await c.promote_chat_member(
            m.chat.id,
            u.id,
            privileges=_demote(),
        )
        await clear_promoter(m.chat.id, u.id)
        _invalidate_cache(m.chat.id, u.id)
        return await m.reply_text(s["ADOK"])
    except Exception:
        return await m.reply_text(s["ADFAIL"])