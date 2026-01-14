import asyncio
import time
from pyrogram import filters, StopPropagation
from pyrogram.enums import ChatMemberStatus, ChatType
from pyrogram.types import ChatPermissions
from datetime import datetime, timedelta

from ArchRobot import arch
from ArchRobot.logger import LOGGER
from strings import get_string
from ArchRobot.db.users import lang, update_user
from ArchRobot.db.settings import get, set

__mod_name__ = "Antiflood"
__help__ = "FLD_HELP"

_L = LOGGER("FLD")
_cnt = {}
_ts = {}
_last = {}
_one = {}
_ntc = {}
_mute = ChatPermissions()


def _s(uid: int):
    return get_string(lang(uid) or "en")


def _fld(cid: int):
    return get(cid, "flood", 0)


def _flt(cid: int):
    return get(cid, "floodt", None)


def _fmd(cid: int):
    return get(cid, "floodm", "ban")


def _fcl(cid: int):
    return get(cid, "floodc", False)


def _pt(t: str) -> int:
    if not t:
        return 0
    u = t[-1].lower()
    try:
        v = int(t[:-1])
    except ValueError:
        return 0
    if u == "m":
        return v * 60
    elif u == "h":
        return v * 3600
    elif u == "d":
        return v * 86400
    elif u == "w":
        return v * 604800
    else:
        try:
            return int(t)
        except ValueError:
            return 0


async def _is_adm(c, cid: int, uid: int) -> bool:
    try:
        m = await c.get_chat_member(cid, uid)
        return m.status in (ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR)
    except Exception:
        return False


async def _act(c, cid: int, uid: int, act: str, dur: int = 0):
    try:
        if act == "ban":
            await c.ban_chat_member(cid, uid)
        elif act == "kick":
            await c.ban_chat_member(cid, uid)
            await c.unban_chat_member(cid, uid)
        elif act == "mute":
            await c.restrict_chat_member(cid, uid, _mute)
        elif act == "tban":
            until = datetime.now() + timedelta(seconds=dur) if dur else None
            await c.ban_chat_member(cid, uid, until_date=until)
        elif act == "tmute":
            until = datetime.now() + timedelta(seconds=dur) if dur else None
            await c.restrict_chat_member(cid, uid, _mute, until_date=until)
    except Exception:
        pass


@arch.on_message(filters.command("flood", prefixes=["/", "!", "."]), group=1)
async def fld_st(c, m):
    if m.chat.type == ChatType.PRIVATE:
        return await m.reply_text(_s(m.from_user.id)["GROUP_ONLY"])
    s = _s(m.from_user.id)
    await update_user(m.from_user.id, m.from_user.username)
    lim = _fld(m.chat.id)
    ft = _flt(m.chat.id)
    md = _fmd(m.chat.id)
    cl = _fcl(m.chat.id)
    if not lim:
        return await m.reply_text(s["FLD_OFF"])
    txt = s["FLD_ST"].format(lim, md, ft[0] if ft else "-", ft[1] if ft else "-", "on" if cl else "off")
    await m.reply_text(txt)


@arch.on_message(filters.command("setflood", prefixes=["/", "!", "."]), group=1)
async def fld_set(c, m):
    if m.chat.type == ChatType.PRIVATE:
        return await m.reply_text(_s(m.from_user.id)["GROUP_ONLY"])
    s = _s(m.from_user.id)
    await update_user(m.from_user.id, m.from_user.username)
    if not await _is_adm(c, m.chat.id, m.from_user.id):
        return
    if len(m.command) < 2:
        return
    v = m.command[1].lower()
    if v in ("off", "no", "0"):
        set(m.chat.id, "flood", 0)
        _cnt.pop(m.chat.id, None)
        _ts.pop(m.chat.id, None)
        _last.pop(m.chat.id, None)
        return await m.reply_text(s["FLD_OFF"])
    try:
        n = int(v)
        if n < 1:
            return
        set(m.chat.id, "flood", n)
        await m.reply_text(s["FLD_SET"].format(n))
    except ValueError:
        return


@arch.on_message(filters.command("setfloodtimer", prefixes=["/", "!", "."]), group=1)
async def fld_tset(c, m):
    if m.chat.type == ChatType.PRIVATE:
        return await m.reply_text(_s(m.from_user.id)["GROUP_ONLY"])
    s = _s(m.from_user.id)
    await update_user(m.from_user.id, m.from_user.username)
    if not await _is_adm(c, m.chat.id, m.from_user.id):
        return
    if len(m.command) < 2:
        return
    v = m.command[1].lower()
    if v in ("off", "no"):
        set(m.chat.id, "floodt", None)
        _ts.pop(m.chat.id, None)
        return await m.reply_text(s["FLD_TOFF"])
    if len(m.command) < 3:
        return
    try:
        cnt = int(m.command[1])
        dur = int(m.command[2])
        if cnt < 1 or dur < 1:
            return
        set(m.chat.id, "floodt", (cnt, dur))
        await m.reply_text(s["FLD_TSET"].format(cnt, dur))
    except ValueError:
        return


@arch.on_message(filters.command("floodmode", prefixes=["/", "!", "."]), group=1)
async def fld_mode(c, m):
    if m.chat.type == ChatType.PRIVATE:
        return await m.reply_text(_s(m.from_user.id)["GROUP_ONLY"])
    s = _s(m.from_user.id)
    await update_user(m.from_user.id, m.from_user.username)
    if not await _is_adm(c, m.chat.id, m.from_user.id):
        return
    if len(m.command) < 2:
        return await m.reply_text(s["FLD_MODE"].format(_fmd(m.chat.id)))
    md = m.command[1].lower()
    if md not in ("ban", "mute", "kick", "tban", "tmute"):
        return
    dur = 0
    if md in ("tban", "tmute") and len(m.command) > 2:
        dur = _pt(m.command[2])
    set(m.chat.id, "floodm", md)
    if dur:
        set(m.chat.id, "floodd", dur)
    await m.reply_text(s["FLD_MODE"].format(md))


@arch.on_message(filters.command("clearflood", prefixes=["/", "!", "."]), group=1)
async def fld_clr(c, m):
    if m.chat.type == ChatType.PRIVATE:
        return await m.reply_text(_s(m.from_user.id)["GROUP_ONLY"])
    s = _s(m.from_user.id)
    await update_user(m.from_user.id, m.from_user.username)
    if not await _is_adm(c, m.chat.id, m.from_user.id):
        return
    if len(m.command) < 2:
        return
    v = m.command[1].lower()
    if v in ("yes", "on"):
        set(m.chat.id, "floodc", True)
        return await m.reply_text(s["FLD_CLR_ON"])
    elif v in ("no", "off"):
        set(m.chat.id, "floodc", False)
        return await m.reply_text(s["FLD_CLR_OFF"])


@arch.on_message(filters.command("fban", prefixes=["/", "!", "."]), group=1)
async def fld_1ban(c, m):
    if m.chat.type == ChatType.PRIVATE:
        return
    if not await _is_adm(c, m.chat.id, m.from_user.id):
        return
    if len(m.command) < 2:
        return
    try:
        cnt = int(m.command[1])
        if cnt < 1:
            return
        k = (m.chat.id, "fban")
        _one[k] = cnt
        await m.reply_text(_s(m.from_user.id)["FLD_1SET"].format("ban", cnt))
        raise StopPropagation
    except ValueError:
        return


@arch.on_message(filters.command("fmute", prefixes=["/", "!", "."]), group=1)
async def fld_1mute(c, m):
    if m.chat.type == ChatType.PRIVATE:
        return
    if not await _is_adm(c, m.chat.id, m.from_user.id):
        return
    if len(m.command) < 2:
        return
    try:
        cnt = int(m.command[1])
        if cnt < 1:
            return
        k = (m.chat.id, "fmute")
        _one[k] = cnt
        await m.reply_text(_s(m.from_user.id)["FLD_1SET"].format("mute", cnt))
    except ValueError:
        return


@arch.on_message(filters.command("fkick", prefixes=["/", "!", "."]), group=1)
async def fld_1kick(c, m):
    if m.chat.type == ChatType.PRIVATE:
        return
    if not await _is_adm(c, m.chat.id, m.from_user.id):
        return
    if len(m.command) < 2:
        return
    try:
        cnt = int(m.command[1])
        if cnt < 1:
            return
        k = (m.chat.id, "fkick")
        _one[k] = cnt
        await m.reply_text(_s(m.from_user.id)["FLD_1SET"].format("kick", cnt))
    except ValueError:
        return


@arch.on_message(filters.command("ftban", prefixes=["/", "!", "."]), group=1)
async def fld_1tban(c, m):
    if m.chat.type == ChatType.PRIVATE:
        return
    if not await _is_adm(c, m.chat.id, m.from_user.id):
        return
    if len(m.command) < 3:
        return
    try:
        cnt = int(m.command[1])
        dur = _pt(m.command[2])
        if cnt < 1 or dur < 1:
            return
        k = (m.chat.id, "ftban")
        _one[k] = (cnt, dur)
        await m.reply_text(_s(m.from_user.id)["FLD_1SET"].format("tban", cnt))
    except ValueError:
        return


@arch.on_message(filters.command("ftmute", prefixes=["/", "!", "."]), group=1)
async def fld_1tmute(c, m):
    if m.chat.type == ChatType.PRIVATE:
        return
    if not await _is_adm(c, m.chat.id, m.from_user.id):
        return
    if len(m.command) < 3:
        return
    try:
        cnt = int(m.command[1])
        dur = _pt(m.command[2])
        if cnt < 1 or dur < 1:
            return
        k = (m.chat.id, "ftmute")
        _one[k] = (cnt, dur)
        await m.reply_text(_s(m.from_user.id)["FLD_1SET"].format("tmute", cnt))
    except ValueError:
        return


async def _del_ntc(cid: int, mid: int, delay: int = 3600):
    await asyncio.sleep(delay)
    if _ntc.get(cid) == mid:
        try:
            await arch.delete_messages(cid, mid)
        except Exception:
            pass
        _ntc.pop(cid, None)


@arch.on_message(filters.group & ~filters.service, group=3)
async def fld_hnd(c, m):
    if not m.from_user:
        return
    if m.from_user.is_bot:
        return
    if m.text and m.text.startswith(("/", "!", ".")):
        return
    cid = m.chat.id
    uid = m.from_user.id
    if await _is_adm(c, cid, uid):
        return
    lim = _fld(cid)
    ft = _flt(cid)
    md = _fmd(cid)
    cl = _fcl(cid)
    dur = get(cid, "floodd", 0)
    hit = False
    one_act = None
    one_dur = 0
    for kk in list(_one.keys()):
        if kk[0] == cid:
            kv = _one[kk]
            if isinstance(kv, tuple):
                kcnt, kdur = kv
            else:
                kcnt, kdur = kv, 0
            if cid not in _cnt:
                _cnt[cid] = {}
            if uid not in _cnt[cid]:
                _cnt[cid][uid] = 0
            _cnt[cid][uid] += 1
            _L.info(f"FLD | cnt inc | chat={cid} user={uid}")
            if _cnt[cid][uid] >= kcnt:
                one_act = kk[1].replace("f", "")
                one_dur = kdur
                _one.pop(kk, None)
                _cnt[cid].pop(uid, None)
                hit = True
                _L.info(f"FLD | 1use consume | chat={cid} user={uid}")
                break
            else:
                if _last.get(cid) != uid:
                    _cnt[cid][uid] = 1
                _last[cid] = uid
                return
    if hit and one_act:
        if cl:
            try:
                await m.delete()
            except Exception:
                pass
        await _act(c, cid, uid, one_act, one_dur)
        _L.info(f"FLD | 1use act | chat={cid} user={uid} act={one_act}")
        try:
            await arch.send_message(cid, _s(uid)["FLD_1USE"].format(one_act))
        except Exception:
            pass
        return
    if not lim and not ft:
        return
    if _last.get(cid) != uid:
        _cnt[cid] = {uid: 1}
        _ts[cid] = {uid: [time.time()]}
        _last[cid] = uid
        return
    if cid not in _cnt:
        _cnt[cid] = {}
    if uid not in _cnt[cid]:
        _cnt[cid][uid] = 0
    _cnt[cid][uid] += 1
    _L.info(f"FLD | cnt inc | chat={cid} user={uid}")
    if ft:
        if cid not in _ts:
            _ts[cid] = {}
        if uid not in _ts[cid]:
            _ts[cid][uid] = []
        now = time.time()
        _ts[cid][uid].append(now)
        _ts[cid][uid] = [t for t in _ts[cid][uid] if now - t <= ft[1]]
        if len(_ts[cid][uid]) >= ft[0]:
            hit = True
            _ts[cid][uid] = []
            _L.info(f"FLD | timer expire | chat={cid} user={uid}")
    if lim and _cnt[cid][uid] >= lim:
        hit = True
        _cnt[cid][uid] = 0
        _L.info(f"FLD | hit | chat={cid} user={uid}")
    if hit:
        if cl:
            try:
                await m.delete()
            except Exception:
                pass
        await _act(c, cid, uid, md, dur)
        _L.info(f"FLD | act | chat={cid} user={uid} act={md}")
        try:
            await arch.send_message(cid, _s(uid)["FLD_HIT"].format(md))
        except Exception:
            pass
