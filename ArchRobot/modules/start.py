

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from ArchRobot import arch
from strings import get_string, languages_present
from ArchRobot.db.users import lang, set_lang, agreed, set_agreed, update_user
import config

def kb_priv(l):
    s = get_string(l)
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(s["AGREE"], callback_data="agree")],
            [InlineKeyboardButton("🌐 Language", callback_data="lang")],
        ]
    )


def kb_start():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("ℹ️ Help", callback_data="help"),
                InlineKeyboardButton("🌐 Language", callback_data="lang"),
            ],
            [
                InlineKeyboardButton(
                    "💬 Support Group", url=f"https://t.me/{config.SUPPORT_GROUP}"
                ),
                InlineKeyboardButton(
                    "📢 Channel", url=f"https://t.me/{config.SUPPORT_CHANNEL}"
                ),
            ],
            [InlineKeyboardButton("✖ Close", callback_data="close")],
        ]
    )


def kb_lang():
    rows, r = [], []
    for c, n in languages_present.items():
        r.append(InlineKeyboardButton(n, callback_data=f"lang_{c}"))
        if len(r) == 2:
            rows.append(r)
            r = []
    if r:
        rows.append(r)
    rows.append([InlineKeyboardButton("◀ Back", callback_data="back")])
    return InlineKeyboardMarkup(rows)


@arch.on_message(filters.command("start") & filters.private)
async def start(_, m):
    uid = m.from_user.id
    username = m.from_user.username
    l = lang(uid) or "en"
    s = get_string(l)

    await update_user(uid, username, l)

    if not agreed(uid):
        await m.reply_text(
            s["PRIVACY"],
            reply_markup=kb_priv(l),
            disable_web_page_preview=True,
        )
        return

    await m.reply_text(
        s["START"].format(m.from_user.first_name, arch.me.first_name),
        reply_markup=kb_start(),
    )


@arch.on_callback_query(filters.regex("^agree$"))
async def agree_cb(_, q):
    uid = q.from_user.id
    l = lang(uid) or "en"
    s = get_string(l)

    set_agreed(uid)

    await q.message.edit_text(
        s["START"].format(q.from_user.first_name, arch.me.first_name),
        reply_markup=kb_start(),
    )


@arch.on_callback_query(filters.regex("^lang$"))
async def lang_open(_, q):
    await q.message.edit_reply_markup(kb_lang())


@arch.on_callback_query(filters.regex("^lang_"))
async def lang_set(_, q):
    l = q.data.split("_", 1)[1]
    set_lang(q.from_user.id, l)
    s = get_string(l)

    if agreed(q.from_user.id):
        await q.message.edit_text(
            s["START"].format(q.from_user.first_name, arch.me.first_name),
            reply_markup=kb_start(),
        )
    else:
        await q.message.edit_text(
            s["PRIVACY"],
            reply_markup=kb_priv(l),
            disable_web_page_preview=True,
        )


@arch.on_callback_query(filters.regex("^back$"))
async def back(_, q):
    uid = q.from_user.id
    l = lang(uid) or "en"
    s = get_string(l)

    if agreed(uid):
        await q.message.edit_text(
            s["START"].format(q.from_user.first_name, arch.me.first_name),
            reply_markup=kb_start(),
        )
    else:
        await q.message.edit_text(
            s["PRIVACY"],
            reply_markup=kb_priv(l),
            disable_web_page_preview=True,
        )


@arch.on_callback_query(filters.regex("^close$"))
async def close(_, q):
    await q.message.delete()