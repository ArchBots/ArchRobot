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

from config.config import MONGO_URI
from ArchRobot.logging import LOGGER


TEMP_MONGODB = "mongodb+srv://archpublic:v8KG2NlkAa70Fx3V@cluster0.whdnitw.mongodb.net/?appName=Cluster0"

logger = LOGGER(__name__)

if not MONGO_URI:
    logger.warning("No MONGO_URI found, using public Arch database")
    uri = TEMP_MONGODB
    db_name = "ArchPublic"
else:
    uri = MONGO_URI
    db_name = "Arch"

_mongo_async = AsyncIOMotorClient(uri)
_mongo_sync = MongoClient(uri)

adb = _mongo_async[db_name]
db = _mongo_sync[db_name]