from telegram import Update
from telegram.ext import ContextTypes
from db.guess import guessDB
from config import OWNER, ADMINS

async def rarity_sticker_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != OWNER and user_id not in ADMINS:
        await update.message.reply_text("✘ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ. ✘")
        return
    
    if not context.args or len(context.args) < 1:
        await update.message.reply_text("✘ ᴜsᴀɢᴇ: /raritystickeradd <rarity_name>")
        return
    
    rarity_name = ' '.join(context.args)
    
    if not update.message.sticker:
        await update.message.reply_text("✘ ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ sᴛɪᴄᴋᴇʀ ᴡɪᴛʜ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ. ✘")
        return
    
    sticker_id = update.message.sticker.file_id
    result = guessDB.add_rarity_sticker(rarity_name, sticker_id)
    
    if result:
        await update.message.reply_text(
            "✨ ᴀᴅᴅᴇᴅ ɴᴇᴡ ʀᴀʀɪᴛʏ sᴛɪᴄᴋᴇʀ.\n"
            f"• ʀᴀʀɪᴛʏ: {rarity_name}\n"
            f"• sᴛɪᴄᴋᴇʀ ɪᴅ: {sticker_id}"
        )
    else:
        await update.message.reply_text(f"✘ ʀᴀʀɪᴛʏ '{rarity_name}' ᴀʟʀᴇᴀᴅʏ ʜᴀs ᴀ sᴛɪᴄᴋᴇʀ. ᴜsᴇ /raritystickeredit ᴛᴏ ᴄʜᴀɴɢᴇ ɪᴛ.")

async def rarity_sticker_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id != OWNER and user_id not in ADMINS:
        await update.message.reply_text("✘ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ᴜsᴇ �ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ. ✘")
        return
    
    if not context.args or len(context.args) < 1:
        await update.message.reply_text("✘ ᴜsᴀɢᴇ: /raritystickeredit <rarity_name>")
        return
    
    rarity_name = ' '.join(context.args)
    
    if not update.message.sticker:
        await update.message.reply_text("✘ ᴘʟᴇᴀsᴇ sᴇɴᴅ ᴀ sᴛɪᴄᴋᴇʀ ᴡɪᴛʜ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")
        return
    
    sticker_id = update.message.sticker.file_id
    result = guessDB.change_rarity_sticker(rarity_name, sticker_id)
    
    if result:
        await update.message.reply_text(
            "🛈 ᴜᴘᴅᴀᴛᴇᴅ ʀᴀʀɪᴛʏ sᴛɪᴄᴋᴇʀ:\n"
            f"• ʀᴀʀɪᴛʏ: {rarity_name}\n"
            f"• ɴᴇᴡ sᴛɪᴄᴋᴇʀ ɪᴅ: {sticker_id}"
        )
    else:
        await update.message.reply_text(f"✘ ʀᴀʀɪᴛʏ '{rarity_name}' ɴᴏᴛ ғᴏᴜɴᴅ. ᴜsᴇ /raritystickeradd ᴛᴏ ᴄʀᴇᴀᴛᴇ ɪᴛ.")

async def rarity_sticker_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    stickers = guessDB.rarity_stickers()
    
    if not stickers:
        await update.message.reply_text("✘ ɴᴏ ʀᴀʀɪᴛʏ sᴛɪᴄᴋᴇʀs ʜᴀᴠᴇ ʙᴇᴇɴ sᴇᴛ ʏᴇᴛ.")
        return
    
    message = "📜 ʀᴀʀɪᴛʏ sᴛɪᴄᴋᴇʀs ʟɪsᴛ:\n\n"
    for rarity, sticker_id in stickers:
        message += f"• {rarity}: {sticker_id}\n"
    
    await update.message.reply_text(message)