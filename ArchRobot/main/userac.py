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


import asyncio, os
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
        return getattr(config, "STRING_SESSIONS", [
            getattr(config, k) for k in dir(config) if k.startswith("STRING")
        ])

    async def _start_one(self, n, s):
        if not s:
            return
        try:
            c = Client(f"ub_{n}", config.API_ID, config.API_HASH, session_string=s, no_updates=True)
            await c.start()
            await self._attach_me(c)
            self.clients.append(c)
        except (RPCError, BadRequest, Forbidden):
            pass

    async def _attach_me(self, c):
        m = await c.get_me()
        c.id, c.username = m.id, m.username
        c.name = f"{m.first_name} {m.last_name}".strip() if m.last_name else m.first_name

    def _next(self) -> Optional[Client]:
        if not self.clients:
            return None
        c = self.clients[self.i % len(self.clients)]
        self.i += 1
        return c

    async def _raw(self, user):
        for _ in self.clients:
            c = self._next()
            try:
                p = await c.resolve_peer(user)
                return await c.invoke(functions.users.GetFullUser(id=p))
            except FloodWait:
                await asyncio.sleep(0)
            except Exception:
                pass
        return None

    def _pack(self, r):
        u, f = r.users[0], r.full_user
        name = f"{u.first_name or ''} {u.last_name or ''}".strip()
        return {
            "id": u.id,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "full_name": f"{name} ({u.id})",
            "username": f"@{u.username}" if u.username else None,
            "user_link": f"https://t.me/{u.username}" if u.username else f"tg://user?id={u.id}",
            "bio": f.about or "",
        }

    async def get_user_info(self, user):
        r = await self._raw(user)
        return self._pack(r) if r else {}

    async def get_bio(self, user):
        d = await self.get_user_info(user)
        return "".join(c for c in d.get("bio", "") if c.isprintable()).lower().strip()

    async def get_pfp(self, user, limit=1, download=False, path="profiles/"):
        os.makedirs(path, exist_ok=True)
        for _ in self.clients:
            c = self._next()
            try:
                return [await self._pfp_one(c, p, download, path)
                        async for p in c.get_chat_photos(user, limit=limit)]
            except FloodWait:
                await asyncio.sleep(0)
            except Exception:
                pass
        return []

    async def _pfp_one(self, c, p, d, path):
        return await c.download_media(p.file_id, f"{path}{p.file_unique_id}.jpg") if d else p.file_id

    def format_info(self, d):
        if not d:
            return "❌ failed"
        link = d["user_link"] if d["username"] else f"[Open profile]({d['user_link']})"
        return (
            "User info:\n"
            f"ID: {d['id']}\n"
            f"First Name: {d['first_name']}\n"
            f"Last Name: {d['last_name'] or 'None'}\n"
            f"Full Name: {d['full_name']}\n"
            f"Username: {d['username'] or 'None'}\n"
            f"User link: {link}"
        )

    def one(self):
        return self.clients[0] if self.clients else None

    def all(self):
        return self.clients


Ub = ArchUb()