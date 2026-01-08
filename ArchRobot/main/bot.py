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


import sys
from pyrogram import Client
from pyrogram.types import BotCommand
import config
from ..logging import LOGGER


class ArchRoBot(Client):
    def __init__(self):
        LOGGER(__name__).info("Starting Bot")
        super().__init__(
            "ArchRobot",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
        )

    async def start(self):
        await super().start()

        me = await self.get_me()
        self.id = me.id
        self.username = me.username
        self.name = (
            f"{me.first_name} {me.last_name}".strip()
            if me.last_name
            else me.first_name
        )

        try:
            await self.send_message(config.LOG_GROUP_ID, "Bot Started")
        except Exception:
            LOGGER(__name__).error(
                "Bot cannot access log group. Add and promote it as admin."
            )
            sys.exit()

        if str(config.SET_CMDS) == "True":
            try:
                await self.set_bot_commands(
                    [BotCommand("ping", "Check bot status")]
                )
            except Exception:
                pass

        m = await self.get_chat_member(config.LOG_GROUP_ID, self.id)
        if m.status != "administrator":
            LOGGER(__name__).error(
                "Bot must be admin in log group"
            )
            sys.exit()

        LOGGER(__name__).info(f"ArchRobot Started as {self.name}")