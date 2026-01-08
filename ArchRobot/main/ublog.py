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
from pyrogram.errors import RPCError, BadRequest, Forbidden
import config
from ..logging import LOGGER

assistants = []
assistantids = []


async def start_assistants():
    LOGGER(__name__).info("Starting Assistant Clients")

    sessions = getattr(config, "STRING_SESSIONS", None)
    if not sessions:
        sessions = [getattr(config, k) for k in dir(config) if k.startswith("STRING")]

    for i, s in enumerate(sessions, 1):
        if not s:
            continue
        try:
            app = Client(
                api_id=config.API_ID,
                api_hash=config.API_HASH,
                session_name=str(s),
                no_updates=True,
            )

            await app.start()

            for chat in ("archbots", "ArchAssociation"):
                try:
                    await app.join_chat(chat)
                except Exception:
                    pass

            try:
                await app.send_message(config.LOG_GROUP_ID, "Assistant Started")
            except Exception:
                LOGGER(__name__).error(
                    f"Assistant Account {i} failed to access log group"
                )
                sys.exit()

            me = await app.get_me()
            app.id = me.id
            app.username = me.username
            app.name = (
                f"{me.first_name} {me.last_name}".strip()
                if me.last_name
                else me.first_name
            )

            assistants.append(app)
            assistantids.append(me.id)

            LOGGER(__name__).info(
                f"Assistant {i} Started as {app.name}"
            )

        except (RPCError, BadRequest, Forbidden) as e:
            LOGGER(__name__).error(f"Assistant {i} failed: {e}")

    return assistants


def assistant_status():
    return {
        "count": len(assistants),
        "ids": assistantids,
    }