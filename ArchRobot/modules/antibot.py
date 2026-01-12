#
# Copyright (c) 2024–2026 ArchBots
#
# This file is part of the ArchRobot project.
# Repository: https://github.com/ArchBots/ArchRobot
#
# Licensed under the MIT License.
# You may obtain a copy of the License in the LICENSE file
# distributed with this source code.
#
# This software is provided "as is", without warranty of any kind,
#

from pyrogram import filters
from pyrogram.enums import MessageEntityType, ChatMemberStatus, ChatType
from pyrogram.types import Message

from ArchRobot import arch
from strings import get_string
from ArchRobot.db.users import lang, update_user
from ArchRobot.db.settings import antibot_mode, set_antibot_mode

__mod_name__ = "Antibot"
__help__ = "ANTIBOTHELP"

_cache = {}


def _s(uid: int):
    return get_string(lang(uid) or "en")


def _get_mode(cid: int) -> str:
    if cid in _cache:
        return _cache[cid]
    mode = antibot_mode(cid) or "off"
    _cache[cid] = mode
    return mode


def _set_mode(cid: int, mode: str):
    _cache[cid] = mode
    set_antibot_mode(cid, mode)


def _has_link_entity(m: Message) -> bool:
    if not m.entities:
        return False
    return any(
        e.type in (MessageEntityType.URL, MessageEntityType.TEXT_LINK)
        for e in m.entities
    )


def _has_invite_link(m: Message) -> bool:
    text = (m.text or m.caption or "").lower()
    return any(x in text for x in ("t.me/", "t.me/+", "joinchat", "telegram.me/"))


def _has_media(m: Message) -> bool:
    return bool(
        m.photo
        or m.video
        or m.document
        or m.animation
        or m.sticker
        or m.audio
        or m.voice
    )


def _has_url_buttons(m: Message) -> bool:
    if not m.reply_markup or not m.reply_markup.inline_keyboard:
        return False
    for row in m.reply_markup.inline_keyboard:
        for btn in row:
            if btn.url:
                return True
    return False


@arch.on_message(filters.command("antibot"))
async def antibot_cmd(c, m: Message):
    # Check if in private chat first
    if m.chat.type == ChatType.PRIVATE:
        s = _s(m.from_user.id)
        return await m.reply_text(s["GROUP_ONLY"])
    
    s = _s(m.from_user.id)
    await update_user(m.from_user.id, m.from_user.username)

    member = await c.get_chat_member(m.chat.id, m.from_user.id)
    if member.status == ChatMemberStatus.OWNER:
        pass  # Owner can always use this command
    elif not member.privileges or not member.privileges.can_delete_messages:
        return await m.reply_text(s["ANTIBOT_NOPERM"])

    if len(m.command) < 2:
        mode = _get_mode(m.chat.id)
        return await m.reply_text(s[f"ANTIBOT_{mode.upper()}"])

    mode = m.command[1].lower()
    if mode not in ("off", "links", "media", "buttons", "all"):
        return await m.reply_text(s["ANTIBOT_USAGE"])

    _set_mode(m.chat.id, mode)
    await m.reply_text(s[f"ANTIBOT_{mode.upper()}"])


@arch.on_message(filters.group)
async def antibot_handler(c, m: Message):
    # Skip commands - check if text starts with / or if there's a bot command entity at offset 0
    if m.text and m.text.startswith("/"):
        return
    
    if m.entities:
        for e in m.entities:
            if e.type == MessageEntityType.BOT_COMMAND and e.offset == 0:
                return  # Return immediately when command found at offset 0

    if not m.from_user or not m.from_user.is_bot:
        return

    if m.from_user.id == arch.me.id:
        return

    mode = _get_mode(m.chat.id)
    if mode == "off":
        return

    should_delete = False

    if mode == "all":
        should_delete = True
    elif mode == "links":
        should_delete = _has_link_entity(m) or _has_invite_link(m)
    elif mode == "media":
        should_delete = _has_media(m)
    elif mode == "buttons":
        should_delete = _has_url_buttons(m)

    if not should_delete:
        return

    try:
        me = await c.get_chat_member(m.chat.id, arch.me.id)
    except Exception:
        return

    if not me.privileges or not me.privileges.can_delete_messages:
        return

    try:
        await m.delete()
    except Exception:
        pass