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


import asyncio
from typing import List, Optional
from pyrogram import Client
from pyrogram.errors import FloodWait, RPCError, BadRequest, Forbidden
from pyrogram.raw import functions
import config


class ArchUb:
    def __init__(self):
        self.clients: List[Client] = []
        self.i = 0

    async def start(self):
        for n, s in enumerate(self._sessions(), 1):
            await self._start_one(n, s)

    def _sessions(self):
        return getattr(
            config,
            "STRING_SESSIONS",
            [getattr(config, k) for k in dir(config) if k.startswith("STRING")]
        )

    async def _start_one(self, n, s):
        if not s:
            return
        try:
            c = Client(
                f"ub_{n}",
                config.API_ID,
                config.API_HASH,
                session_string=s,
                no_updates=True
            )
            await c.start()
            self.clients.append(c)
        except (RPCError, BadRequest, Forbidden):
            pass

    def _next(self) -> Optional[Client]:
        if not self.clients:
            return None
        c = self.clients[self.i % len(self.clients)]
        self.i += 1
        return c

    async def _raw_bio(self, user):
        for _ in self.clients:
            c = self._next()
            try:
                p = await c.resolve_peer(user)
                r = await c.invoke(functions.users.GetFullUser(id=p))
                return r.full_user.about or ""
            except FloodWait:
                await asyncio.sleep(0)
            except Exception:
                pass
        return ""

    async def get_bio(self, user) -> str:
        bio = await self._raw_bio(user)
        return "".join(c for c in bio if c.isprintable()).lower().strip()

    def one(self):
        return self.clients[0] if self.clients else None

    def all(self):
        return self.clients


Ub = ArchUb()