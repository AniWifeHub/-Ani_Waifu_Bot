from telegram import Update,InlineKeyboardMarkup,InlineKeyboardButton
from telegram.ext import ContextTypes
from frequently_used_functions import check_membership
from db.users import userDB
import json
import random

starts = 'data/start.json'

def load():
    with open(starts,'r',encoding='utf-8') as file:
        return json.load(file)

async def check_register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("start", url="https://t.me/Ani_Waifu_Bot")]])

    if userDB.exist_user(user.id):
        return True
    else:
        sent_message = await update.effective_message.reply_text(
            text="✘ Yᴏᴜ Aʀᴇ ɴOᴛ ʀEɢɪꜱTᴇʀEᴅ ɪN ᴅAᴛᴀBᴀꜱᴇ! PʟᴇᴀSᴇ ꜱTᴀRᴛ ʙOᴛ. ✘",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        
        context.job_queue.run_once(
            callback=delete_messages,
            when=15,
            data={
                'chat_id': update.effective_chat.id,
                'bot_message_id': sent_message.message_id,
                'user_message_id': update.effective_message.message_id
            }
        )
        return False

async def delete_messages(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    try:
        await context.bot.delete_message(
            chat_id=job.data['chat_id'],
            message_id=job.data['bot_message_id']
        )
        
        await context.bot.delete_message(
            chat_id=job.data['chat_id'],
            message_id=job.data['user_message_id']
        )
    except Exception as e:
        print(f"Error deleting messages: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_membership(update, context):
        return
    
    s_d = load()

    phore = random.choice(s_d['phores'])

    userDB.create_user(update.effective_user.id)
    await update.effective_message.reply_photo(
        photo=phore,
        caption=(
            f"✧･ﾟ: *✧･ﾟ:* Aɴɪ Wᴀɪғᴜ Bᴏᴛ Wᴇʟᴄᴏᴍᴇs Yᴏᴜ! *:･ﾟ✧*:･ﾟ✧\n\n"
            f"Hᴇʟᴘ Mᴇɴᴜ:\n\n"
            f"- /guess ➔ Sᴛᴀʀᴛ ɢᴜᴇssɪɴɢ ɢᴀᴍᴇ\n"
            f"- /harem ➔ Vɪᴇᴡ ʏᴏᴜʀ ʜᴀʀᴇᴍ\n"
            f"- /gift ➔ Gɪғᴛ ᴀ ᴄʜᴀʀᴀᴄᴛᴇʀ\n"
            f"- /tops ➔ Vɪᴇᴡ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ\n\n"
            f"Hᴀᴠᴇ ᴀ ɢʀᴇᴀᴛ ᴅᴀʏ! ♡"
            ),
        parse_mode="Markdown"
    )