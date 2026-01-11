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

#
# Copyright (c) 2024–2026 ArchBots
#
# This file is part of the ArchRobot project.
# Repository: https://github.com/ArchBots/ArchRobot
#
# Licensed under the MIT License.
#

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus, MessageEntityType
from pyrogram.types import ChatAdministratorRights

from ArchRobot import arch
from strings import get_string
from ArchRobot.db.users import lang, update_user
from ArchRobot.db.settings import anon, err, set_anon, set_err


__mod_name__ = "Admin"
__help__ = "AHELP"


def _s(uid):
    return get_string(lang(uid) or "en")


async def _is_admin(c, cid, uid):
    m = await c.get_chat_member(cid, uid)
    return m.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)


def _delegate(bot):
    return ChatAdministratorRights(
        **{
            k: v
            for k, v in vars(bot).items()
            if k not in ("can_promote_members", "is_anonymous")
        }
    )


def _demote_all():
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


@arch.on_message(filters.command("promote") & filters.group)
async def promote(c, m):
    s = _s(m.from_user.id)
    await update_user(m.from_user.id, m.from_user.username)

    if not await _is_admin(c, m.chat.id, arch.me.id):
        return await m.reply_text(s["ABOT"])

    me = await c.get_chat_member(m.chat.id, arch.me.id)
    if not me.privileges or not me.privileges.can_promote_members:
        return await m.reply_text(s["ABOTP"])

    if not anon(m.chat.id) and not await _is_admin(c, m.chat.id, m.from_user.id):
        if err(m.chat.id):
            await m.reply_text(s["AUSER"])
        return

    u = await _target(c, m)
    if not u:
        return await m.reply_text(s["ATARGET"])

    await update_user(u.id, u.username)

    cm = await c.get_chat_member(m.chat.id, u.id)
    if cm.status == ChatMemberStatus.ADMINISTRATOR:
        if cm.promoted_by and cm.promoted_by.id != arch.me.id:
            return await m.reply_text(s["AALREADY"])
        return await m.reply_text(s["APOK"])

    try:
        await c.promote_chat_member(
            m.chat.id,
            u.id,
            privileges=_delegate(me.privileges),
        )
        await m.reply_text(s["APOK"])
    except Exception:
        await m.reply_text(s["APFAIL"])


@arch.on_message(filters.command("demote") & filters.group)
async def demote(c, m):
    s = _s(m.from_user.id)
    await update_user(m.from_user.id, m.from_user.username)

    if not await _is_admin(c, m.chat.id, arch.me.id):
        return await m.reply_text(s["ABOT"])

    me = await c.get_chat_member(m.chat.id, arch.me.id)
    if not me.privileges or not me.privileges.can_promote_members:
        return await m.reply_text(s["ABOTP"])

    if not anon(m.chat.id) and not await _is_admin(c, m.chat.id, m.from_user.id):
        if err(m.chat.id):
            await m.reply_text(s["AUSERP"])
        return

    u = await _target(c, m)
    if not u:
        return await m.reply_text(s["ATARGET"])

    await update_user(u.id, u.username)

    cm = await c.get_chat_member(m.chat.id, u.id)
    if cm.status != ChatMemberStatus.ADMINISTRATOR:
        return await m.reply_text(s["ADFAIL"])

    try:
        await c.promote_chat_member(
            m.chat.id,
            u.id,
            privileges=_demote_all(),
        )
        await m.reply_text(s["ADOK"])
    except Exception:
        await m.reply_text(s["ADFAIL"])


@arch.on_message(filters.command("adminlist") & filters.group)
async def adminlist(c, m):
    s = _s(m.from_user.id)
    out = []
    async for x in c.get_chat_members(m.chat.id, filter="administrators"):
        out.append(x.user.mention)
    await m.reply_text("\n".join(out) or s["ALIST_EMPTY"])


@arch.on_message(filters.command("admincache") & filters.group)
async def admincache(_, m):
    s = _s(m.from_user.id)
    await m.reply_text(s["ACACHE"])


@arch.on_message(filters.command("anonadmin") & filters.group)
async def anonadmin(_, m):
    s = _s(m.from_user.id)
    if len(m.command) < 2:
        return
    v = m.command[1].lower() in ("on", "yes", "true")
    set_anon(m.chat.id, v)
    await m.reply_text(s["AANON_ON"] if v else s["AANON_OFF"])


@arch.on_message(filters.command("adminerror") & filters.group)
async def adminerror(_, m):
    s = _s(m.from_user.id)
    if len(m.command) < 2:
        return
    v = m.command[1].lower() in ("on", "yes", "true")
    set_err(m.chat.id, v)
    await m.reply_text(s["AERR_ON"] if v else s["AERR_OFF"])