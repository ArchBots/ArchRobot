from pyrogram import Client

from config.config import API_ID, API_HASH, BOT_TOKEN
from ArchRobot.logger import LOGGER

logger = LOGGER(__name__)

logger.info("Initializing ArchRobot")

app = Client(
    "ArchRobot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)

logger.info("ArchRobot initialized successfully")
