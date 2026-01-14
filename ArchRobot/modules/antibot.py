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

import asyncio
from pyrogram import filters
from pyrogram.enums import MessageEntityType, ChatMemberStatus, ChatType
from pyrogram.types import Message
from pyrogram.handlers import MessageHandler

from ArchRobot import arch
from ArchRobot.main.userac import Ub
from ArchRobot.logger import LOGGER
from strings import get_string
from ArchRobot.db.users import lang, update_user
from ArchRobot.db.settings import antibot_mode, set_antibot_mode
from ArchRobot.modules.anti_bio import check_bio, _ensure_ub_in_chat

__mod_name__ = "Antibot"
__help__ = "ANTIBOTHELP"

_L = LOGGER("AB")
_cache = {}
_ntc = {}
_ntc_task = {}
_hnd = False


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


@arch.on_message(filters.command("antibot", prefixes=["/", "!", "."]), group=1)
async def antibot_cmd(c, m: Message):
    if m.chat.type == ChatType.PRIVATE:
        s = _s(m.from_user.id)
        return await m.reply_text(s["GROUP_ONLY"])
    
    s = _s(m.from_user.id)
    await update_user(m.from_user.id, m.from_user.username)

    member = await c.get_chat_member(m.chat.id, m.from_user.id)
    if member.status == ChatMemberStatus.OWNER:
        pass
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

    if mode != "off":
        uc = Ub.one()
        if uc:
            joined = await _ensure_ub_in_chat(uc, m.chat.id)
            if not joined:
                _L.info(f"AB | assistant join fail | chat={m.chat.id}")


async def _ab_watch(_, m: Message):
    if m.text and m.text.startswith(("/", "!", ".")):
        return
    if m.entities:
        for e in m.entities:
            if e.type == MessageEntityType.BOT_COMMAND and e.offset == 0:
                return
    mode = _get_mode(m.chat.id)
    if mode == "off":
        return
    if not m.from_user:
        return
    if not m.from_user.is_bot:
        if await check_bio(m):
            return
        return
    if m.from_user.id == arch.id:
        _L.info(f"AB | skip self | chat={m.chat.id}")
        return
    _L.info(f"AB | bot msg | chat={m.chat.id}")
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
    cid = m.chat.id
    mid = m.id
    try:
        await arch.delete_messages(cid, mid)
        _L.info(f"AB | bot msg del | chat={cid}")
    except Exception:
        pass
    await _send_ntc(cid)


def reg_ab_hnd():
    global _hnd
    if _hnd:
        return
    uc = Ub.one()
    if not uc:
        return
    uc.add_handler(MessageHandler(_ab_watch, filters.group), group=2)
    _hnd = True


async def _del_ntc(cid: int, mid: int):
    await asyncio.sleep(3600)
    if _ntc.get(cid) == mid:
        try:
            await arch.delete_messages(cid, mid)
            _L.info(f"AB | ntc del | chat={cid}")
        except Exception:
            pass
        _ntc.pop(cid, None)
        _ntc_task.pop(cid, None)


async def _send_ntc(cid: int):
    if cid in _ntc:
        if cid in _ntc_task:
            _ntc_task[cid].cancel()
        _ntc_task[cid] = asyncio.create_task(_del_ntc(cid, _ntc[cid]))
        _L.info(f"AB | ntc reuse | chat={cid}")
        return
    s = get_string("en")
    try:
        msg = await arch.send_message(cid, s["AB_WARN"], disable_notification=True)
        _ntc[cid] = msg.id
        _ntc_task[cid] = asyncio.create_task(_del_ntc(cid, msg.id))
        _L.info(f"AB | ntc sent | chat={cid}")
    except Exception:
        pass