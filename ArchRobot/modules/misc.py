from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update
from telegram.ext import CallbackContext, CommandHandler, Filters

from ArchRobot import dispatcher
from ArchRobot.modules.disable import DisableAbleCommandHandler
from ArchRobot.modules.helper_funcs.chat_status import user_admin

MARKDOWN_HELP = f"""
ᴍᴀʀᴋᴅᴏᴡɴ ɪs ᴀ ᴠᴇʀʏ ᴘᴏᴡᴇʀғᴜʟ ғᴏʀᴍᴀᴛᴛɪɴɢ ᴛᴏᴏʟ sᴜᴘᴘᴏʀᴛᴇᴅ ʙʏ ᴛᴇʟᴇɢʀᴀᴍ. {dispatcher.bot.first_name} ʜᴀs sᴏᴍᴇ ᴇɴʜᴀɴᴄᴇᴍᴇɴᴛs, ᴛᴏ ᴍᴀᴋᴇ sᴜʀᴇ ᴛʜᴀᴛ \n
sᴀᴠᴇᴅ ᴍᴇssᴀɢᴇs ᴀʀᴇ ᴄᴏʀʀᴇᴄᴛʟʏ ᴘᴀʀsᴇᴅ, ᴀɴᴅ ᴛᴏ ᴀʟʟᴏᴡ ʏᴏᴜ ᴛᴏ ᴄʀᴇᴀᴛᴇ ʙᴜᴛᴛᴏɴs.

• <code>_ɪᴛᴀʟɪᴄ_</code>: ᴡʀᴀᴘᴘɪɴɢ ᴛᴇxᴛ ᴡɪᴛʜ '_' ᴡɪʟʟ ᴘʀᴏᴅᴜᴄᴇ ɪᴛᴀʟɪᴄ ᴛᴇxᴛ
• <code>*ʙᴏʟᴅ*</code>: ᴡʀᴀᴘᴘɪɴɢ ᴛᴇxᴛ ᴡɪᴛʜ '*' ᴡɪʟʟ ᴘʀᴏᴅᴜᴄᴇ ʙᴏʟᴅ ᴛᴇxᴛ
• <code>`ᴄᴏᴅᴇ`</code>: ᴡʀᴀᴘᴘɪɴɢ ᴛᴇxᴛ ᴡɪᴛʜ '`' ᴡɪʟʟ ᴘʀᴏᴅᴜᴄᴇ ᴍᴏɴᴏsᴘᴀᴄᴇᴅ ᴛᴇxᴛ, ᴀʟsᴏ ᴋɴᴏᴡɴ ᴀs 'code'
• <code>[sᴏᴍᴇᴛᴇxᴛ](sᴏᴍᴇᴜʀʟ)</code>: ᴛʜɪs ᴡɪʟʟ ᴄʀᴇᴀᴛᴇ ᴀ ʟɪɴᴋ - ᴛʜᴇ ᴍᴇssᴀɢᴇ ᴡɪʟʟ ᴊᴜsᴛ sʜᴏᴡ <code>sᴏᴍᴇᴛᴇxᴛ</code>, \n
ᴀɴᴅ ᴛᴀᴘᴘɪɴɢ ᴏɴ ɪᴛ ᴡɪʟʟ ᴏᴘᴇɴ ᴛʜᴇ ᴘᴀɢᴇ ᴀᴛ <code>sᴏᴍᴇᴜʀʟ</code>.
<b>ᴇxᴀᴍᴘʟᴇ:</b><code>[ᴛᴇsᴛ](example.com)</code>

• <code>[ʙᴜᴛᴛᴏɴᴛᴇxᴛ](buttonurl:someurl)</code>: ᴛʜɪs ɪs ᴀ sᴘᴇᴄɪᴀʟ ᴇɴʜᴀɴᴄᴇᴍᴇɴᴛ ᴛᴏ ᴀʟʟᴏᴡ ᴜsᴇʀs ᴛᴏ ʜᴀᴠᴇ ᴛᴇʟᴇɢʀᴀᴍ \n
ʙᴜᴛᴛᴏɴs ɪɴ ᴛʜᴇɪʀ ᴍᴀʀᴋᴅᴏᴡɴ. <code>ʙᴜᴛᴛᴏɴᴛᴇxᴛ</code> ᴡɪʟʟ ʙᴇ ᴡʜᴀᴛ ɪs ᴅɪsᴘʟᴀʏᴇᴅ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴ, ᴀɴᴅ <code>sᴏᴍᴇᴜʀʟ</code> \n
ᴡɪʟʟ ʙᴇ ᴛʜᴇ ᴜʀʟ ᴡʜɪᴄʜ ɪs ᴏᴘᴇɴᴇᴅ.
<b>ᴇxᴀᴍᴘʟᴇ:</b> <code>[ᴛʜɪs ɪs ᴀ ʙᴜᴛᴛᴏɴ](buttonurl://google.com)</code>

ɪғ ʏᴏᴜ ᴡᴀɴᴛ ᴍᴜʟᴛɪᴘʟᴇ ʙᴜᴛᴛᴏɴs ᴏɴ ᴛʜᴇ sᴀᴍᴇ ʟɪɴᴇ, ᴜsᴇ :sᴀᴍᴇ, ᴀs sᴜᴄʜ:
<code>[ᴏɴᴇ](buttonurl://google.com)
[ᴛᴡᴏ](buttonurl://google.com:same )</code>
ᴛʜɪs ᴡɪʟʟ ᴄʀᴇᴀᴛᴇ ᴛᴡᴏ ʙᴜᴛᴛᴏɴs ᴏɴ ᴀ sɪɴɢʟᴇ ʟɪɴᴇ, ɪɴsᴛᴇᴀᴅ ᴏғ ᴏɴᴇ ʙᴜᴛᴛᴏɴ ᴘᴇʀ ʟɪɴᴇ.

ᴋᴇᴇᴘ ɪɴ ᴍɪɴᴅ ᴛʜᴀᴛ ʏᴏᴜʀ ᴍᴇssᴀɢᴇ <b>ᴍᴜsᴛ</b> ᴄᴏɴᴛᴀɪɴ sᴏᴍᴇ ᴛᴇxᴛ ᴏᴛʜᴇʀ ᴛʜᴀɴ ᴊᴜsᴛ ᴀ ʙᴜᴛᴛᴏɴ!
"""


@user_admin
def echo(update: Update, context: CallbackContext):
    args = update.effective_message.text.split(None, 1)
    message = update.effective_message

    if message.reply_to_message:
        message.reply_to_message.reply_text(
            args[1], parse_mode="MARKDOWN", disable_web_page_preview=True
        )
    else:
        message.reply_text(
            args[1], quote=False, parse_mode="MARKDOWN", disable_web_page_preview=True
        )
    message.delete()


def markdown_help_sender(update: Update):
    update.effective_message.reply_text(MARKDOWN_HELP, parse_mode=ParseMode.HTML)
    update.effective_message.reply_text(
        "Try forwarding the following message to me, and you'll see, and Use #test!"
    )
    update.effective_message.reply_text(
        "/save test This is a markdown test. _italics_, *bold*, code, "
        "[URL](example.com) [button](buttonurl:github.com) "
        "[button2](buttonurl://google.com:same)"
    )


def markdown_help(update: Update, context: CallbackContext):
    if update.effective_chat.type != "private":
        update.effective_message.reply_text(
            "Contact me in pm",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "Markdown help",
                            url=f"t.me/{context.bot.username}?start=markdownhelp",
                        )
                    ]
                ]
            ),
        )
        return
    markdown_help_sender(update)


__help__ = """
*ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅs:*
*ᴍᴀʀᴋᴅᴏᴡɴ:*
 ❍ /markdownhelp*:* ǫᴜɪᴄᴋ sᴜᴍᴍᴀʀʏ ᴏғ ʜᴏᴡ ᴍᴀʀᴋᴅᴏᴡɴ ᴡᴏʀᴋs ɪɴ ᴛᴇʟᴇɢʀᴀᴍ - ᴄᴀɴ ᴏɴʟʏ ʙᴇ ᴄᴀʟʟᴇᴅ ɪɴ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛs
*ʀᴇᴀᴄᴛ:*
 ❍ /react *:* ʀᴇᴀᴄᴛs ᴡɪᴛʜ ᴀ ʀᴀɴᴅᴏᴍ ʀᴇᴀᴄᴛɪᴏɴ 
*ᴜʀʙᴀɴ ᴅɪᴄᴛᴏɴᴀʀʏ:*
 ❍ /ud <ᴡᴏʀᴅ>*:* ᴛʏᴘᴇ ᴛʜᴇ ᴡᴏʀᴅ ᴏʀ ᴇxᴘʀᴇssɪᴏɴ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ sᴇᴀʀᴄʜ ᴜsᴇ
*ᴡɪᴋɪᴘᴇᴅɪᴀ:*
 ❍ /wiki  <ǫᴜᴇʀʏ>*:* ᴡɪᴋɪᴘᴇᴅɪᴀ ʏᴏᴜʀ ǫᴜᴇʀʏ
"""

ECHO_HANDLER = DisableAbleCommandHandler(
    "echo", echo, filters=Filters.chat_type.groups, run_async=True
)
MD_HELP_HANDLER = CommandHandler("markdownhelp", markdown_help, run_async=True)

dispatcher.add_handler(ECHO_HANDLER)
dispatcher.add_handler(MD_HELP_HANDLER)

__mod_name__ = "Exᴛʀᴀs"
__command_list__ = ["id", "echo"]
__handlers__ = [
    ECHO_HANDLER,
    MD_HELP_HANDLER,
]
