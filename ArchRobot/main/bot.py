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
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import BotCommand

import config
from ArchRobot.logger import LOGGER
from ArchRobot.db import federations, filt
from ArchRobot.main.userac import Ub


class ArchRoBot(Client):
    def __init__(self):
        self.log = LOGGER(__name__)
        self.log.info("Initializing ArchRoBot")

        super().__init__(
            name="ArchRobot",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
        )

    async def start(self, *args, **kwargs):
        await super().start(*args, **kwargs)

        self.log.info("Initializing MongoDB indexes")
        try:
            await federations.create_indexes()
            await filt.create_indexes()
        except Exception as e:
            self.log.error(f"Failed to create MongoDB indexes: {e}")
            sys.exit(1)

        me = await self.get_me()
        self.id = me.id
        self.username = me.username
        self.name = (
            f"{me.first_name} {me.last_name}".strip()
            if me.last_name
            else me.first_name
        )

        try:
            await self.send_message(
                config.LOG_GROUP_ID,
                f"{self.name} started"
            )
        except Exception:
            self.log.error("Bot cannot access log group")
            sys.exit(1)

        try:
            member = await self.get_chat_member(
                config.LOG_GROUP_ID,
                self.id
            )
            if member.status not in (
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER,
            ):
                raise PermissionError
        except Exception:
            self.log.error("Bot must be admin in log group")
            sys.exit(1)

        if str(config.SET_CMDS).lower() == "true":
            try:
                await self.set_bot_commands(
                    [
                        BotCommand("start", "Start the bot"),
                        BotCommand("ping", "Check bot status"),
                        BotCommand("help", "Get help"),
                        BotCommand("newfed", "Create a federation"),
                        BotCommand("myfeds", "List your federations"),
                        BotCommand("chatfed", "Show chat federation"),
                        BotCommand("joinfed", "Join a federation"),
                        BotCommand("leavefed", "Leave federation"),
                        BotCommand("fban", "Federation ban user"),
                        BotCommand("funban", "Federation unban user"),
                    ]
                )
            except Exception:
                pass

        await Ub.start()
        if Ub.clients:
            self.log.info("assistant started")
            try:
                await self.send_message(config.LOG_GROUP_ID, "assistant started")
            except Exception:
                pass
        from ArchRobot.modules.antibot import reg_ab_hnd
        reg_ab_hnd()
        self.log.info(f"ArchRoBot started as {self.name}")

    async def stop(self, *args, **kwargs):
        await super().stop(*args, **kwargs)