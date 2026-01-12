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
from ArchRobot.db.settings import err, set_anon, set_err


__mod_name__ = "Admin"
__help__ = "AHELP"


def _s(uid):
    return get_string(lang(uid) or "en")


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


@arch.on_message(filters.command("promote") & filters.group)
async def promote(c, m):
    s = _s(m.from_user.id)
    await update_user(m.from_user.id, m.from_user.username)

    bot = await c.get_chat_member(m.chat.id, arch.me.id)
    if not bot.privileges or not bot.privileges.can_promote_members:
        return await m.reply_text(s["ABOTP"])

    provider = await c.get_chat_member(m.chat.id, m.from_user.id)
    if provider.status != ChatMemberStatus.OWNER:
        if not provider.privileges or not provider.privileges.can_promote_members:
            if err(m.chat.id):
                await m.reply_text(s["AUSERP"])
            return

    u = await _target(c, m)
    if not u:
        return await m.reply_text(s["ATARGET"])

    await update_user(u.id, u.username)
    target = await c.get_chat_member(m.chat.id, u.id)

    if target.status == ChatMemberStatus.OWNER:
        return await m.reply_text(s["AOWNER"])
    
    if target.status == ChatMemberStatus.ADMINISTRATOR:
        return await m.reply_text(s["AALREADY"])

    title = " ".join(m.command[2:]) if len(m.command) > 2 else None

    try:
        # If provider is owner, they have all rights, so just use bot's privileges
        if provider.status == ChatMemberStatus.OWNER:
            rights = bot.privileges
        else:
            rights = _mix(bot.privileges, provider.privileges)
        
        await c.promote_chat_member(
            m.chat.id,
            u.id,
            privileges=rights,
        )
        if title:
            await c.set_administrator_title(m.chat.id, u.id, title)

        await m.reply_text(s["APOK"])
    except Exception:
        await m.reply_text(s["APFAIL"])


@arch.on_message(filters.command("demote") & filters.group)
async def demote(c, m):
    s = _s(m.from_user.id)
    await update_user(m.from_user.id, m.from_user.username)

    bot = await c.get_chat_member(m.chat.id, arch.me.id)
    if not bot.privileges or not bot.privileges.can_promote_members:
        return await m.reply_text(s["ABOTP"])

    provider = await c.get_chat_member(m.chat.id, m.from_user.id)
    if provider.status != ChatMemberStatus.OWNER:
        if not provider.privileges or not provider.privileges.can_promote_members:
            if err(m.chat.id):
                await m.reply_text(s["AUSERP"])
            return

    u = await _target(c, m)
    if not u:
        return await m.reply_text(s["ATARGET"])

    target = await c.get_chat_member(m.chat.id, u.id)
    if target.status != ChatMemberStatus.ADMINISTRATOR:
        return await m.reply_text(s["ADFAIL"])

    try:
        await c.promote_chat_member(
            m.chat.id,
            u.id,
            privileges=_demote(),
        )
        await m.reply_text(s["ADOK"])
    except Exception:
        await m.reply_text(s["ADFAIL"])