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


from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pyrogram import Client

from config.config import API_ID, API_HASH, BOT_TOKEN, MONGO_URI
from ArchRobot.logging import LOGGER


TEMP_MONGODB = "mongodb+srv://archpublic:v8KG2NlkAa70Fx3V@cluster0.whdnitw.mongodb.net/?appName=Cluster0"

logger = LOGGER(__name__)


def _get_username():
    app = Client(
        "ArchRobotTemp",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN,
        in_memory=True,
    )
    app.start()
    me = app.get_me()
    app.stop()
    return me.username


if not MONGO_URI:
    logger.warning("No MONGO_DB_URI found, using public Arch database")

    username = _get_username()

    _mongo_async = AsyncIOMotorClient(TEMP_MONGODB)
    _mongo_sync = MongoClient(TEMP_MONGODB)

    mongodb = _mongo_async[username]
    pymongodb = _mongo_sync[username]

else:
    _mongo_async = AsyncIOMotorClient(MONGO_URI)
    _mongo_sync = MongoClient(MONGO_URI)

    mongodb = _mongo_async.Arch
    pymongodb = _mongo_sync.Arch