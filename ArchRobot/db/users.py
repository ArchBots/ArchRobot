import re
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

__mod_name__ = "Antibio"
__help__ = "ANTIBIO_HELP"

_L = LOGGER("ANTIBIO")

_URL_RE = re.compile(r"(https?://|t\.me/|telegram\.me/|(?<![a-zA-Z0-9])@[a-zA-Z][a-zA-Z0-9_]{4,})", re.I)


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
    except (ChannelPrivate, ChannelInvalid, PeerIdInvalid) as e:
        _L.info(f"ANTIBIO | ub check fail | chat={cid} | err={type(e).__name__}")
    except Exception as e:
        _L.info(f"ANTIBIO | ub check err | chat={cid} | err={type(e).__name__}")
        return False
    try:
        ch = await arch.get_chat(cid)
        if getattr(ch, 'join_by_request', False):
            _L.info(f"ANTIBIO | join_by_request | chat={cid}")
            return False
        lnk = getattr(ch, 'invite_link', None)
        if lnk:
            try:
                await uc.join_chat(lnk)
                _L.info(f"ANTIBIO | ub joined via existing link | chat={cid}")
                return True
            except UserAlreadyParticipant:
                return True
            except InviteRequestSent:
                _L.info(f"ANTIBIO | invite request sent | chat={cid}")
                return False
            except (FloodWait, ChatAdminRequired) as e:
                _L.info(f"ANTIBIO | ub join fail | chat={cid} | err={type(e).__name__}")
                return False
            except Exception as e:
                _L.info(f"ANTIBIO | ub join err | chat={cid} | err={type(e).__name__}")
                # fallthrough: existing link might be invalid, try creating new one
        try:
            me = await arch.get_chat_member(cid, arch.id)
            if not (me.privileges and me.privileges.can_invite_users):
                _L.info(f"ANTIBIO | bot no invite perm | chat={cid}")
                return False
        except Exception as e:
            _L.info(f"ANTIBIO | bot check err | chat={cid} | err={type(e).__name__}")
            return False
        try:
            inv = await arch.create_chat_invite_link(cid, creates_join_request=False)
            lnk = inv.invite_link
        except (ChatAdminRequired, FloodWait) as e:
            _L.info(f"ANTIBIO | create link fail | chat={cid} | err={type(e).__name__}")
            return False
        except Exception as e:
            _L.info(f"ANTIBIO | create link err | chat={cid} | err={type(e).__name__}")
            return False
        if not lnk:
            _L.info(f"ANTIBIO | no link created | chat={cid}")
            return False
        try:
            await uc.join_chat(lnk)
            _L.info(f"ANTIBIO | ub joined via new link | chat={cid}")
            return True
        except UserAlreadyParticipant:
            return True
        except InviteRequestSent:
            _L.info(f"ANTIBIO | invite request sent | chat={cid}")
            return False
        except (FloodWait, ChatAdminRequired) as e:
            _L.info(f"ANTIBIO | ub join new link fail | chat={cid} | err={type(e).__name__}")
            return False
        except Exception as e:
            _L.info(f"ANTIBIO | ub join new link err | chat={cid} | err={type(e).__name__}")
            return False
    except Exception as e:
        _L.info(f"ANTIBIO | ensure ub err | chat={cid} | err={type(e).__name__}")
        return False


async def _get_bio(uid: int) -> str:
    try:
        u = await arch.get_users(uid)
        if u and hasattr(u, "bio") and u.bio:
            return u.bio.lower().strip()
    except Exception:
        pass
    bio = await Ub.get_bio(uid)
    if bio:
        return bio
    return ""


async def _del_msg(cid: int, mid: int):
    try:
        await arch.delete_messages(cid, mid)
        return True
    except Exception:
        pass
    cs = Ub.all()
    for uc in cs:
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
        await arch.send_message(cid, f"[{uid}](tg://user?id={uid}) {txt}", disable_notification=True)
    except Exception:
        cs = Ub.all()
        for uc in cs:
            if await _ensure_ub_in_chat(uc, cid):
                try:
                    await uc.send_message(cid, f"[{uid}](tg://user?id={uid}) {txt}", disable_notification=True)
                    return
                except Exception:
                    pass


async def _is_adm(cid: int, uid: int) -> bool:
    try:
        m = await arch.get_chat_member(cid, uid)
        return m.status in (ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR)
    except Exception:
        return False


async def check_bio(m) -> bool:
    if not m.from_user:
        return False
    if m.from_user.is_bot:
        return False
    uid = m.from_user.id
    cid = m.chat.id
    if await _is_adm(cid, uid):
        return False
    bio = await _get_bio(uid)
    if not _has_bio_link(bio):
        return False
    mid = m.id
    await _del_msg(cid, mid)
    await _warn_user(cid, uid)
    return True
"