from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import Message
from ArchRobot import (
    BOT_NAME,
    BOT_USERNAME,
    LOGGER,
    OWNER_ID,
    START_IMG,
    SUPPORT_CHAT,
    TOKEN,
    StartTime,
    dispatcher,
    pbot,
    telethn,
    updater,
    MONGO_DB_URI,
    API_ID,
    API_HASH
)

from ArchRobot import BOT_NAME,OWNER_ID
from ArchRobot import pbot as app
@app.on_message(
    filters.command(["con", "var"]) & filters.user(OWNER_ID)
)
async def get_vars(_, message: Message):
    try:
        await app.send_message(
            chat_id=int(OWNER_ID),
            text=f"""<u>**{BOT_NAME} ᴄᴏɴғɪɢ ᴠᴀʀɪᴀʙʟᴇs :**</u>

**ʙᴏᴛ_ᴛᴏᴋᴇɴ :** `{TOKEN}`
**sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ :** `{SUPPORT_CHAT}`
**Sᴛᴀʀᴛ Iᴍᴀɢᴇ :** `{START_IMG}`
**Aᴘɪ Iᴅ :** `{API_ID}`
**Aᴘɪ Hᴀsʜ :** `{API_HASH}` 
**Mᴏɴɢᴏ Uʀʟ :** `{MONGO_DB_URI}`   




""")
    except:
        return await message.reply_text("» ғᴀɪʟᴇᴅ ᴛᴏ sᴇɴᴅ ᴛʜᴇ ᴄᴏɴғɪɢ ᴠᴀʀɪᴀʙʟᴇs.")
    if message.chat.type != ChatType.PRIVATE:
        await message.reply_text(
            "» ᴘʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴘᴍ, ɪ'ᴠᴇ sᴇɴᴛ ᴛʜᴇ ᴄᴏɴғɪɢ ᴠᴀʀɪᴀʙʟᴇs ᴛʜᴇʀᴇ."
        )
