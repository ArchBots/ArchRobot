#
# Copyright (c) 2024–2026 ArchBots
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

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from ArchRobot import arch
from strings import get_string
from ArchRobot.db.users import lang
from ArchRobot.modules import ALL_MODULES


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


@arch.on_message(filters.command("help") & filters.private)
async def help_cmd(_, m):
    s = _s(m.from_user.id)
    await m.reply_text(
        s.get("HELP", "Choose a module:"),
        reply_markup=kb_help(),
    )


@arch.on_callback_query(filters.regex("^help_"))
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


@arch.on_callback_query(filters.regex("^help_back$"))
async def help_back(_, q):
    s = _s(q.from_user.id)
    await q.message.edit_text(
        s.get("HELP", "Choose a module:"),
        reply_markup=kb_help(),
    )


@arch.on_callback_query(filters.regex("^close$"))
async def close(_, q):
    await q.message.delete()


if __name__ == "__main__":
    arch.run()