import uuid
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus, ChatType

from ArchRobot import arch
from strings import get_string
from ArchRobot.db.users import lang, update_user
from ArchRobot.db import federations


__mod_name__ = "Federation"
__help__ = "FHELP"


def _s(uid):
    return get_string(lang(uid) or "en")


async def _is_admin(c, cid, uid):
    m = await c.get_chat_member(cid, uid)
    return m.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)


async def _is_owner(c, cid, uid):
    m = await c.get_chat_member(cid, uid)
    return m.status == ChatMemberStatus.OWNER


async def _target(c, m):
    if m.reply_to_message:
        return m.reply_to_message.from_user
    if len(m.command) < 2:
        return None
    try:
        return await c.get_users(m.command[1])
    except Exception:
        return None


@arch.on_message(filters.command("newfed") & filters.private)
async def newfed(_, m):
    s = _s(m.from_user.id)

    if len(m.command) < 2:
        return await m.reply_text(s["FNAME_REQ"])

    fed_name = m.text.split(None, 1)[1].strip()
    fed_id = str(uuid.uuid4())

    success = await federations.create_federation(fed_id, fed_name, m.from_user.id)

    if success:
        await m.reply_text(s["FCREATED"].format(fed_id, fed_name))
    else:
        await m.reply_text(s["FEXISTS"])


@arch.on_message(filters.command("renamefed"))
async def renamefed(_, m):
    s = _s(m.from_user.id)

    if len(m.command) < 2:
        return await m.reply_text(s["FNAME_REQ"])

    new_name = m.text.split(None, 1)[1].strip()

    user_feds = await federations.get_user_federations(m.from_user.id)
    owner_feds = [f for f in user_feds if f["owner_id"] == m.from_user.id]

    if not owner_feds:
        return await m.reply_text(s["FNOFEDS"])

    fed = owner_feds[0]
    success = await federations.rename_federation(fed["federation_id"], new_name)

    if success:
        await m.reply_text(s["FRENAMED"].format(new_name))
    else:
        await m.reply_text(s["FNOTFOUND"])


@arch.on_message(filters.command("deletefed"))
async def deletefed(_, m):
    s = _s(m.from_user.id)

    user_feds = await federations.get_user_federations(m.from_user.id)
    owner_feds = [f for f in user_feds if f["owner_id"] == m.from_user.id]

    if not owner_feds:
        return await m.reply_text(s["FNOFEDS"])

    fed = owner_feds[0]
    success = await federations.delete_federation(fed["federation_id"])

    if success:
        await m.reply_text(s["FDELETED"].format(fed["name"]))
    else:
        await m.reply_text(s["FNOTFOUND"])


@arch.on_message(filters.command("fedinfo"))
async def fedinfo(_, m):
    s = _s(m.from_user.id)

    fed_id = None
    if len(m.command) > 1:
        fed_id = m.command[1]
    elif m.chat.type != ChatType.PRIVATE:
        fed_id = await federations.get_chat_federation(m.chat.id)

    if not fed_id:
        return await m.reply_text(s["FCHATNOLINK"])

    fed = await federations.get_federation(fed_id)
    if not fed:
        return await m.reply_text(s["FNOTFOUND"])

    chats = await federations.get_fed_chats(fed_id)
    bans = await federations.get_fed_bans(fed_id)

    await m.reply_text(
        s["FINFO"].format(
            fed["federation_id"],
            fed["name"],
            fed["owner_id"],
            len(chats),
            len(bans)
        )
    )


@arch.on_message(filters.command("fedadmins"))
async def fedadmins(_, m):
    s = _s(m.from_user.id)

    fed_id = None
    if len(m.command) > 1:
        fed_id = m.command[1]
    elif m.chat.type != ChatType.PRIVATE:
        fed_id = await federations.get_chat_federation(m.chat.id)

    if not fed_id:
        return await m.reply_text(s["FCHATNOLINK"])

    fed = await federations.get_federation(fed_id)
    if not fed:
        return await m.reply_text(s["FNOTFOUND"])

    admins = [str(fed["owner_id"])] + [str(aid) for aid in fed.get("admin_ids", [])]
    await m.reply_text(s["FADMINS"].format("\n".join(admins)))


@arch.on_message(filters.command("myfeds"))
async def myfeds(_, m):
    s = _s(m.from_user.id)

    user_feds = await federations.get_user_federations(m.from_user.id)

    if not user_feds:
        return await m.reply_text(s["FNOFEDS"])

    fed_list = []
    for fed in user_feds:
        role = "Owner" if fed["owner_id"] == m.from_user.id else "Admin"
        fed_list.append(f"{fed['name']} ({fed['federation_id']}) - {role}")

    await m.reply_text(s["FMYFEDS"].format("\n".join(fed_list)))


@arch.on_message(filters.command("chatfed") & filters.group)
async def chatfed(_, m):
    s = _s(m.from_user.id)

    fed_id = await federations.get_chat_federation(m.chat.id)

    if not fed_id:
        return await m.reply_text(s["FCHATNOLINK"])

    fed = await federations.get_federation(fed_id)
    if not fed:
        return await m.reply_text(s["FNOTFOUND"])

    await m.reply_text(s["FCHATINFO"].format(fed_id, fed["name"]))


@arch.on_message(filters.command("joinfed") & filters.group)
async def joinfed(c, m):
    s = _s(m.from_user.id)

    if not await _is_owner(c, m.chat.id, m.from_user.id):
        return await m.reply_text(s["FOWNERONLY"])

    if not await _is_admin(c, m.chat.id, arch.me.id):
        return await m.reply_text(s["FBOTNOTADM"])

    if len(m.command) < 2:
        return await m.reply_text(s["FID_REQ"])

    fed_id = m.command[1]

    fed = await federations.get_federation(fed_id)
    if not fed:
        return await m.reply_text(s["FNOTFOUND"])

    existing_fed = await federations.get_chat_federation(m.chat.id)
    if existing_fed:
        return await m.reply_text(s["FALREADY"])

    success = await federations.link_chat(fed_id, m.chat.id, m.from_user.id)

    if success:
        await m.reply_text(s["FJOINED"].format(fed["name"]))
    else:
        await m.reply_text(s["AERR"])


@arch.on_message(filters.command("leavefed") & filters.group)
async def leavefed(c, m):
    s = _s(m.from_user.id)

    if not await _is_owner(c, m.chat.id, m.from_user.id):
        return await m.reply_text(s["FOWNERONLY"])

    fed_id = await federations.get_chat_federation(m.chat.id)

    if not fed_id:
        return await m.reply_text(s["FCHATNOLINK"])

    success = await federations.unlink_chat(m.chat.id)

    if success:
        await m.reply_text(s["FLEFT"])
    else:
        await m.reply_text(s["AERR"])


@arch.on_message(filters.command("fban"))
async def fban(c, m):
    s = _s(m.from_user.id)

    await update_user(m.from_user.id, m.from_user.username)

    fed_id = None

    if m.chat.type != ChatType.PRIVATE:
        fed_id = await federations.get_chat_federation(m.chat.id)
        if not fed_id:
            return await m.reply_text(s["FCHATNOFED"])
    else:
        user_feds = await federations.get_user_federations(m.from_user.id)
        if not user_feds:
            return await m.reply_text(s["FNOFEDS"])
        fed_id = user_feds[0]["federation_id"]

    if not await federations.is_fed_admin(fed_id, m.from_user.id):
        return await m.reply_text(s["FNOTADMIN"])

    if m.chat.type != ChatType.PRIVATE:
        if not await _is_admin(c, m.chat.id, arch.me.id):
            return await m.reply_text(s["FBOTNOTADM"])

    u = await _target(c, m)
    if not u:
        return await m.reply_text(s["FUSER_REQ"])

    await update_user(u.id, u.username)

    reason = s["FBANREAS0"]
    if len(m.command) > 2:
        reason = m.text.split(None, 2)[2].strip()

    await federations.fed_ban_user(fed_id, u.id, reason, m.from_user.id)

    fed_chats = await federations.get_fed_chats(fed_id)
    for chat_id in fed_chats:
        try:
            await c.ban_chat_member(chat_id, u.id)
        except Exception:
            pass

    fed = await federations.get_federation(fed_id)
    await m.reply_text(s["FBANNED"].format(u.mention, fed["name"]))


@arch.on_message(filters.command("funban"))
async def funban(c, m):
    s = _s(m.from_user.id)

    await update_user(m.from_user.id, m.from_user.username)

    fed_id = None

    if m.chat.type != ChatType.PRIVATE:
        fed_id = await federations.get_chat_federation(m.chat.id)
        if not fed_id:
            return await m.reply_text(s["FCHATNOFED"])
    else:
        user_feds = await federations.get_user_federations(m.from_user.id)
        if not user_feds:
            return await m.reply_text(s["FNOFEDS"])
        fed_id = user_feds[0]["federation_id"]

    if not await federations.is_fed_admin(fed_id, m.from_user.id):
        return await m.reply_text(s["FNOTADMIN"])

    if m.chat.type != ChatType.PRIVATE:
        if not await _is_admin(c, m.chat.id, arch.me.id):
            return await m.reply_text(s["FBOTNOTADM"])

    u = await _target(c, m)
    if not u:
        return await m.reply_text(s["FUSER_REQ"])

    await update_user(u.id, u.username)

    if not await federations.is_fed_banned(fed_id, u.id):
        return await m.reply_text(s["FNOTBANNED"])

    await federations.fed_unban_user(fed_id, u.id)

    fed_chats = await federations.get_fed_chats(fed_id)
    for chat_id in fed_chats:
        try:
            await c.unban_chat_member(chat_id, u.id)
        except Exception:
            pass

    fed = await federations.get_federation(fed_id)
    await m.reply_text(s["FUNBANNED"].format(u.mention, fed["name"]))


@arch.on_message(filters.command("fbanlist") & filters.group)
async def fbanlist(_, m):
    s = _s(m.from_user.id)

    fed_id = await federations.get_chat_federation(m.chat.id)

    if not fed_id:
        return await m.reply_text(s["FCHATNOFED"])

    if not await federations.is_fed_admin(fed_id, m.from_user.id):
        return await m.reply_text(s["FNOTADMIN"])

    bans = await federations.get_fed_bans(fed_id)

    if not bans:
        return await m.reply_text(s["FBANLIST0"])

    ban_list = []
    for ban in bans:
        reason = ban["reason_key"]
        ban_list.append(f"User ID: {ban['user_id']} - {reason}")

    await m.reply_text(s["FBANLIST"].format("\n".join(ban_list)))


@arch.on_message(filters.command("fstat"))
async def fstat(c, m):
    s = _s(m.from_user.id)

    await update_user(m.from_user.id, m.from_user.username)

    u = await _target(c, m)
    if not u:
        return await m.reply_text(s["FUSER_REQ"])

    await update_user(u.id, u.username)

    user_bans = await federations.get_user_fed_bans(u.id)

    if not user_bans:
        return await m.reply_text(s["FSTATNOBAN"].format(u.mention))

    fed_list = []
    for ban in user_bans:
        fed = await federations.get_federation(ban["federation_id"])
        if fed:
            reason = ban["reason_key"]
            fed_list.append(f"• {fed['name']} (ID: {fed['federation_id']})\n  Reason: {reason}")

    await m.reply_text(s["FSTATBAN"].format(u.mention, "\n\n".join(fed_list)))


@arch.on_chat_member_updated()
async def fed_enforce(c, update):
    if not update.new_chat_member:
        return

    if update.new_chat_member.status not in (
        ChatMemberStatus.MEMBER,
        ChatMemberStatus.RESTRICTED,
    ):
        return

    chat_id = update.chat.id
    user_id = update.new_chat_member.user.id

    fed_id = await federations.get_chat_federation(chat_id)

    if not fed_id:
        return

    if await federations.is_fed_banned(fed_id, user_id):
        try:
            await c.ban_chat_member(chat_id, user_id)
            fed = await federations.get_federation(fed_id)
            s = get_string("en")
            await c.send_message(chat_id, s["FBANENF"].format(fed["name"]))
        except Exception:
            pass
