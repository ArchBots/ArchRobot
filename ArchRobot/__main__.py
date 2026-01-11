from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config.config import API_ID, API_HASH, BOT_TOKEN
from strings import get_string
from ArchRobot.db.users import lang
from ArchRobot.modules import ALL_MODULES


app = Client(
    "ArchRobot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)


HELPABLE = {}

for m in ALL_MODULES:
    mod = __import__(f"ArchRobot.modules.{m}", fromlist=["*"])
    if hasattr(mod, "__mod_name__") and hasattr(mod, "__help__"):
        HELPABLE[mod.__mod_name__] = mod


def _s(uid):
    return get_string(lang(uid) or "en")


def kb_help():
    rows, r = [], []
    for name in sorted(HELPABLE):
        r.append(InlineKeyboardButton(name, callback_data=f"help_{name}"))
        if len(r) == 2:
            rows.append(r)
            r = []
    if r:
        rows.append(r)
    rows.append([InlineKeyboardButton("✖ Close", callback_data="close")])
    return InlineKeyboardMarkup(rows)


@app.on_message(filters.command("help") & filters.private)
async def help_cmd(_, m):
    s = _s(m.from_user.id)
    await m.reply_text(
        s.get("HELP", "Choose a module:"),
        reply_markup=kb_help(),
    )


@app.on_callback_query(filters.regex("^help_"))
async def help_cb(_, q):
    name = q.data.split("_", 1)[1]
    s = _s(q.from_user.id)

    mod = HELPABLE.get(name)
    if not mod:
        return

    key = mod.__help__
    txt = s.get(key, "No help available.")

    await q.message.edit_text(
        txt,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("◀ Back", callback_data="help_back")]]
        ),
        disable_web_page_preview=True,
    )


@app.on_callback_query(filters.regex("^help_back$"))
async def help_back(_, q):
    s = _s(q.from_user.id)
    await q.message.edit_text(
        s.get("HELP", "Choose a module:"),
        reply_markup=kb_help(),
    )


@app.on_callback_query(filters.regex("^close$"))
async def close(_, q):
    await q.message.delete()


if __name__ == "__main__":
    app.run()