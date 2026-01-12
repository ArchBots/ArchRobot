from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import MessageEntityType

from ArchRobot import arch
from strings import get_string
from ArchRobot.db.users import lang, update_user
from ArchRobot.db.filt import (
    create_filter, delete_filter, delete_all_filters,
    get_chat_filters, find_or_create_reply, get_reply,
    find_matching_filter
)
from ArchRobot.utils.params import check_permission, is_bot_admin, PermissionLevel
from ArchRobot.utils.filt import parse_trigger, expand_fillings, has_filling, expand_command_filling


__mod_name__ = "Filters"
__help__ = "FILT_HELP"


def _s(uid):
    return get_string(lang(uid) or "en")


def _is_cmd(m: Message) -> bool:
    if not m.text:
        return False
    if m.entities:
        for e in m.entities:
            if e.type == MessageEntityType.BOT_COMMAND and e.offset == 0:
                return True
    return m.text.startswith("/")


def _get_media(msg):
    media_map = {
        "sticker": msg.sticker,
        "photo": msg.photo,
        "video": msg.video,
        "document": msg.document,
        "animation": msg.animation
    }
    
    for mtype, media in media_map.items():
        if media:
            cap = getattr(msg, "caption", None) or "" if mtype != "sticker" else None
            return mtype, media.file_id, media.file_unique_id, cap
    
    return "text", None, None, msg.text if msg.text else ""


@arch.on_message(filters.command("filter") & filters.group)
async def filter_cmd(c, m: Message):
    s = _s(m.from_user.id)
    await update_user(m.from_user.id, m.from_user.username)
    
    if not await is_bot_admin(c, m.chat.id, arch.me.id):
        return await m.reply_text(s.get("FBOT", "I need admin rights."))
    
    if not await check_permission(c, m.chat.id, m.from_user.id, PermissionLevel.ADMIN):
        return
    
    if len(m.command) < 2:
        return await m.reply_text(s.get("FUSAGE", "Usage: /filter <trigger> <reply>"))
    
    args = m.text.split(None, 1)[1]
    parts = args.split(None, 1)
    
    if len(parts) < 2:
        if not m.reply_to_message:
            return await m.reply_text(s.get("FUSAGE", "Usage: /filter <trigger> <reply>"))
        trig_str = parts[0]
        reply_msg = m.reply_to_message
        reply_txt = None
    else:
        trig_str = parts[0]
        reply_txt = parts[1]
        reply_msg = m.reply_to_message
    
    trigs = parse_trigger(trig_str)
    if not trigs:
        return await m.reply_text(s.get("FINV", "Invalid trigger."))
    
    cnt = 0
    for traw, tnorm, flgs in trigs:
        rtype, fid, fuid, cont = _get_media(reply_msg) if reply_msg else ("text", None, None, reply_txt or "")
        
        rid = await find_or_create_reply(rtype, cont, fid, fuid)
        if await create_filter(m.chat.id, traw, tnorm, flgs, rid, m.from_user.id):
            cnt += 1
    
    if cnt > 0:
        msg = s.get("FADD", "Filter added: {0}").format(trigs[0][0]) if cnt == 1 else s.get("FADDM", "Added {0} filters.").format(cnt)
        await m.reply_text(msg)
    else:
        await m.reply_text(s.get("FFAIL", "Failed to add filter."))


@arch.on_message(filters.command("stop") & filters.group)
async def stop_cmd(c, m: Message):
    s = _s(m.from_user.id)
    await update_user(m.from_user.id, m.from_user.username)
    
    if not await is_bot_admin(c, m.chat.id, arch.me.id):
        return await m.reply_text(s.get("FBOT", "I need admin rights."))
    
    if not await check_permission(c, m.chat.id, m.from_user.id, PermissionLevel.ADMIN):
        return
    
    if len(m.command) < 2:
        return await m.reply_text(s.get("FSUSAGE", "Usage: /stop <trigger>"))
    
    trig_str = m.text.split(None, 1)[1]
    trigs = parse_trigger(trig_str)
    
    if not trigs:
        return await m.reply_text(s.get("FINV", "Invalid trigger."))
    
    cnt = sum(1 for _, tnorm, _ in trigs if await delete_filter(m.chat.id, tnorm))
    
    if cnt > 0:
        msg = s.get("FREM", "Filter removed: {0}").format(trigs[0][0]) if cnt == 1 else s.get("FREMM", "Removed {0} filters.").format(cnt)
        await m.reply_text(msg)
    else:
        await m.reply_text(s.get("FNOT", "Filter not found."))


@arch.on_message(filters.command("stopall") & filters.group)
async def stopall_cmd(c, m: Message):
    s = _s(m.from_user.id)
    await update_user(m.from_user.id, m.from_user.username)
    
    if not await is_bot_admin(c, m.chat.id, arch.me.id):
        return await m.reply_text(s.get("FBOT", "I need admin rights."))
    
    if not await check_permission(c, m.chat.id, m.from_user.id, PermissionLevel.OWNER):
        return await m.reply_text(s.get("FOWN", "Owner only."))
    
    cnt = await delete_all_filters(m.chat.id)
    
    if cnt > 0:
        await m.reply_text(s.get("FREMA", "Removed {0} filters.").format(cnt))
    else:
        await m.reply_text(s.get("FNONE", "No filters."))


@arch.on_message(filters.command("filters") & filters.group)
async def filters_cmd(c, m: Message):
    s = _s(m.from_user.id)
    await update_user(m.from_user.id, m.from_user.username)
    
    flist = await get_chat_filters(m.chat.id)
    
    if not flist:
        return await m.reply_text(s.get("FNONE", "No filters."))
    
    items = []
    for f in flist:
        trig = f["trigger_raw"]
        flgs = f.get("flags", [])
        if flgs:
            trig = f"{':'.join(flgs)}:{trig}"
        items.append(f" - {trig}")
    
    await m.reply_text(s.get("FLIST", "Filters:\n{0}").format("\n".join(items)))


def _should_reply_to_original(reply_content: str, replied_msg) -> bool:
    return has_filling(reply_content, "{replytag}") and replied_msg is not None


@arch.on_message(filters.group & filters.text & ~filters.command(["filter", "stop", "stopall", "filters"]))
async def filter_handler(c, m: Message):
    if _is_cmd(m) or not m.text:
        return

    filt = await find_matching_filter(m.chat.id, m.text)
    if not filt:
        return

    rdata = await get_reply(filt["reply_id"])
    if not rdata:
        return

    rtype = rdata["reply_type"]
    cont = rdata.get("content", "")
    fid = rdata.get("file_id")

    umention = m.from_user.mention
    rtag = m.reply_to_message.from_user.mention if m.reply_to_message and m.reply_to_message.from_user else None

    if cont:
        cont = expand_fillings(cont, umention, replytag_user=rtag)
        cont = expand_command_filling(cont)

    reply_to = m.reply_to_message if _should_reply_to_original(rdata.get("content", ""), m.reply_to_message) else m

    try:
        send_map = {
            "text": lambda: reply_to.reply_text(cont),
            "sticker": lambda: reply_to.reply_sticker(fid),
            "photo": lambda: reply_to.reply_photo(fid, caption=cont or None),
            "video": lambda: reply_to.reply_video(fid, caption=cont or None),
            "document": lambda: reply_to.reply_document(fid, caption=cont or None),
            "animation": lambda: reply_to.reply_animation(fid, caption=cont or None)
        }

        if rtype in send_map:
            await send_map[rtype]()
    except Exception:
        pass