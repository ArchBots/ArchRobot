import re
from pyrogram import filters
from pyrogram.errors import (
    FloodWait,
    ChatAdminRequired,
    UserNotParticipant,
    UserAlreadyParticipant,
    InviteRequestSent,
    ChannelPrivate,
    ChannelInvalid,
    PeerIdInvalid,
)
from pyrogram.enums import ChatMemberStatus

from ArchRobot import arch
from ArchRobot.main.userac import Ub
from ArchRobot.logger import LOGGER
from strings import get_string
from ArchRobot.db.users import lang
from ArchRobot.db.antibio import get as antibio_enabled, enable, disable


__mod_name__ = "Antibio"
__help__ = "ANTIBIO_HELP"

_L = LOGGER("ANTIBIO")

_URL_RE = re.compile(
    r"(https?://|t\.me/|telegram\.me/|(?<![a-zA-Z0-9])@[a-zA-Z][a-zA-Z0-9_]{4,})",
    re.I,
)


def _s(uid: int):
    return get_string(lang(uid) or "en")


def _has_bio_link(bio: str) -> bool:
    if not bio:
        return False
    return bool(_URL_RE.search(bio))


async def _ensure_ub_in_chat(uc, cid: int):
    if not uc:
        return False
    try:
        await uc.get_chat_member(cid, (await uc.get_me()).id)
        return True
    except UserNotParticipant:
        pass
    except (ChannelPrivate, ChannelInvalid, PeerIdInvalid):
        return False
    except Exception:
        return False
    try:
        ch = await arch.get_chat(cid)
        if getattr(ch, "join_by_request", False):
            return False
        lnk = getattr(ch, "invite_link", None)
        if lnk:
            try:
                await uc.join_chat(lnk)
                return True
            except UserAlreadyParticipant:
                return True
            except InviteRequestSent:
                return False
            except Exception:
                pass
        me = await arch.get_chat_member(cid, arch.id)
        if not (me.privileges and me.privileges.can_invite_users):
            return False
        inv = await arch.create_chat_invite_link(cid, creates_join_request=False)
        if not inv.invite_link:
            return False
        try:
            await uc.join_chat(inv.invite_link)
            return True
        except UserAlreadyParticipant:
            return True
        except Exception:
            return False
    except Exception:
        return False


async def _get_bio(uid: int) -> str:
    try:
        u = await arch.get_users(uid)
        if u and u.bio:
            return u.bio.lower().strip()
    except Exception:
        pass
    bio = await Ub.get_bio(uid)
    return bio or ""


async def _del_msg(cid: int, mid: int):
    try:
        await arch.delete_messages(cid, mid)
        return True
    except Exception:
        pass
    for uc in Ub.all():
        if await _ensure_ub_in_chat(uc, cid):
            try:
                await uc.delete_messages(cid, mid)
                return True
            except Exception:
                pass
    return False


async def _warn_user(cid: int, uid: int):
    s = _s(uid)
    txt = s.get("ANTIBIO_WARN", "You cannot message in this chat. Remove bio link.")
    try:
        await arch.send_message(
            cid,
            f"[{uid}](tg://user?id={uid}) {txt}",
            disable_notification=True,
        )
    except Exception:
        for uc in Ub.all():
            if await _ensure_ub_in_chat(uc, cid):
                try:
                    await uc.send_message(
                        cid,
                        f"[{uid}](tg://user?id={uid}) {txt}",
                        disable_notification=True,
                    )
                    return
                except Exception:
                    pass


async def _is_adm(cid: int, uid: int) -> bool:
    try:
        m = await arch.get_chat_member(cid, uid)
        return m.status in (
            ChatMemberStatus.OWNER,
            ChatMemberStatus.ADMINISTRATOR,
        )
    except Exception:
        return False


async def check_bio(m) -> bool:
    if not m.from_user or m.from_user.is_bot:
        return False

    cid = m.chat.id
    if not antibio_enabled(cid):
        return False

    uid = m.from_user.id
    if await _is_adm(cid, uid):
        return False

    bio = await _get_bio(uid)
    if not _has_bio_link(bio):
        return False

    await _del_msg(cid, m.id)
    await _warn_user(cid, uid)
    return True


@arch.on_message(filters.command("antibio") & filters.group)
async def antibio_cmd(_, m):
    if not m.from_user:
        return

    cid = m.chat.id
    uid = m.from_user.id

    if not await _is_adm(cid, uid):
        return await m.reply_text("Admins only.")

    if len(m.command) < 2:
        return await m.reply_text("Usage: /antibio on | off")

    arg = m.command[1].lower()

    if arg == "on":
        if enable(cid):
            await m.reply_text("✅ Antibio enabled.")
        else:
            await m.reply_text("ℹ️ Antibio is already enabled.")

    elif arg == "off":
        if disable(cid):
            await m.reply_text("❌ Antibio disabled.")
        else:
            await m.reply_text("ℹ️ Antibio is already disabled.")

    else:
        await m.reply_text("Usage: /antibio on | off")