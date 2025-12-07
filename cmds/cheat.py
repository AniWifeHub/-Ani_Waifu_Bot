from telegram import Update
from telegram.ext import ContextTypes
from db.games import gamesDB
from db.cheat import CheatDB
from config import OWNER,ADMINS

async def name(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message.reply_to_message:
        await update.effective_message.reply_text(
            "Bᴀᴋᴀᴀ!! Dᴏɴ'ᴛ Fᴏʀɢᴇᴛ ᴛO ʀEᴘLʏ~!"
        )
        return

    chat_id = update.effective_chat.id

    if gamesDB.check_exist_guess_game(chat_id):
        guess_game = gamesDB.get_guess_game(chat_id)
        char_name = guess_game['name']
        await update.effective_message.reply_text(
            f"🌟 𝗧𝗵𝗲 𝗖𝗵𝗮𝗿𝗮𝗰𝘁𝗲𝗿 *Name* 𝗜𝘀: `{char_name}` 🌟",
            parse_mode='Markdown'
        )
    else:
        await update.effective_message.reply_text(
            "Bᴀᴋᴀᴀ!! 𝗧𝗵𝗲𝗿𝗲 𝗶𝘀 𝗻𝗼 𝗴𝗮𝗺𝗲 𝗶𝗻 𝗽𝗿𝗼𝗴𝗿𝗲𝘀𝘀~!"
        )

async def add_bypass(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id not in [OWNER] + ADMINS:
        return

    if not update.effective_message.reply_to_message:
        await update.effective_message.reply_text(
            "Bᴀᴋᴀᴀ!! ʏᴏᴜ ʜAᴠᴇ ᴛO ʀEᴘLʏ Tᴏ sᴏMᴇᴏNᴇ~!"
        )
        return

    target_id = update.effective_message.reply_to_message.from_user.id
    CheatDB.add_bypass(target_id)
    await update.effective_message.reply_text(f"~ 𝗕𝘆𝗽𝗮𝘀𝘀 User({target_id}) *Added!*",parse_mode='Markdown')

async def remove_bypass(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id not in [OWNER] + ADMINS:
        return

    if not update.effective_message.reply_to_message:
        await update.effective_message.reply_text(
            "Bᴀᴋᴀᴀ!! ʏᴏᴜ ʜAᴠᴇ ᴛO ʀEᴘLʏ Tᴏ sᴏMᴇᴏNᴇ~!"
        )
        return

    target_id = update.effective_message.reply_to_message.from_user.id
    CheatDB.remove_bypass(target_id)
    await update.effective_message.reply_text(f"~ 𝗕𝘆𝗽𝗮𝘀𝘀 User({target_id}) *Removed!*",parse_mode='Markdown')

async def clear_bypass(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id not in [OWNER] + ADMINS:
        return

    CheatDB.clear_bypass()
    await update.effective_message.reply_text("~ 𝗔𝗹𝗹 𝗕𝘆𝗽𝗮𝘀𝘀𝗲𝘀 *Cleared!*")