from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import ChatPrivileges

from ArchRobot import arch
from strings import get_string
from ArchRobot.db.users import lang
from ArchRobot.db.settings import anon, err, set_anon, set_err


__mod_name__ = "Admin"
__help__ = "AHELP"


def _s(uid):
    return get_string(lang(uid) or "en")


async def _is_admin(c, cid, uid):
    m = await c.get_chat_member(cid, uid)
    return m.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)


async def _target(c, m):
    if m.reply_to_message:
        return m.reply_to_message.from_user
    if len(m.command) < 2:
        return None
    try:
        return await c.get_users(m.command[1])
    except Exception:
        return None


@arch.on_message(filters.command("promote") & filters.group)
async def promote(c, m):
    s = _s(m.from_user.id)

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

    cm = await c.get_chat_member(m.chat.id, u.id)
    if cm.status == ChatMemberStatus.ADMINISTRATOR:
        if cm.promoted_by and cm.promoted_by.id != arch.me.id:
            return await m.reply_text(s["AALREADY"])
        return await m.reply_text(s["APOK"])

    try:
        await c.promote_chat_member(
            m.chat.id,
            u.id,
            privileges=ChatPrivileges(
                can_manage_chat=True,
                can_delete_messages=True,
                can_manage_video_chats=True,
                can_restrict_members=True,
                can_invite_users=True,
                can_pin_messages=True,
            ),
        )
        await m.reply_text(s["APOK"])
    except Exception:
        await m.reply_text(s["APFAIL"])


@arch.on_message(filters.command("demote") & filters.group)
async def demote(c, m):
    s = _s(m.from_user.id)

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

    cm = await c.get_chat_member(m.chat.id, u.id)
    if cm.status != ChatMemberStatus.ADMINISTRATOR:
        return await m.reply_text(s["ADFAIL"])

    try:
        await c.promote_chat_member(
            m.chat.id,
            u.id,
            privileges=ChatPrivileges(),
        )
        await m.reply_text(s["ADOK"])
    except Exception:
        await m.reply_text(s["ADFAIL"])


@arch.on_message(filters.command("adminlist") & filters.group)
async def adminlist(c, m):
    out = []
    async for x in c.get_chat_members(m.chat.id, filter="administrators"):
        out.append(x.user.mention)
    await m.reply_text("\n".join(out) or "—")


@arch.on_message(filters.command("admincache") & filters.group)
async def admincache(_, m):
    await m.reply_text("Admin cache refreshed.")


@arch.on_message(filters.command("anonadmin") & filters.group)
async def anonadmin(_, m):
    if len(m.command) < 2:
        return
    v = m.command[1].lower() in ("on", "yes", "true")
    set_anon(m.chat.id, v)
    await m.reply_text(
        "Anon admin enabled." if v else "Anon admin disabled."
    )


@arch.on_message(filters.command("adminerror") & filters.group)
async def adminerror(_, m):
    if len(m.command) < 2:
        return
    v = m.command[1].lower() in ("on", "yes", "true")
    set_err(m.chat.id, v)
    await m.reply_text(
        "Admin errors enabled." if v else "Admin errors disabled."
    )