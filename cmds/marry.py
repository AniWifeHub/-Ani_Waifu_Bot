import random
import asyncio
from db.guess import guessDB
from db.harem import haremDB
from db.users import userDB
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from typing import Dict
from Fonter import to_small_caps

COOLDOWNS: Dict[int, datetime] = {}
FAILED = ["Is ɴOᴛ RᴇᴀDʏ ʏEᴛ!", "Rᴀɴ ᴀWᴀʏ..."]
NOT_FAILED1 = ["Tᴡᴏ ʜEᴀʀTs, Oɴᴇ sᴏUʟ!", "CᴏɴɢʀᴀTs! Yᴏᴜ'ʀᴇ sTᴜᴄᴋ ɴOᴡ!"]
NOT_FAILED2 = ["Nᴏ ʀEᴛᴜRɴs,Nᴏ RᴇғUɴᴅs - ᴊUsᴛ ɪNғɪɴIᴛᴇ CᴜᴅᴅLᴇs!", "Yᴏᴜʀ ʟᴏVᴇ sTᴏʀʏ ʙEɢɪɴs ᴛᴏDᴀʏ..."]

async def marry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    now = datetime.now()

    if user.id in COOLDOWNS and COOLDOWNS[user.id] > now:
        remaining = COOLDOWNS[user.id] - now
        minutes, seconds = divmod(int(remaining.total_seconds()), 60)
        await update.message.reply_text(
            f"⏳ Yᴏᴜ ᴀʀᴇ ᴏɴ ᴄᴏᴏʟᴅᴏᴡɴ! Tʀʏ ᴀɢᴀɪɴ ɪɴ {minutes}m {seconds}s."
        )
        return
    
    game_result = random.randint(1, 101)
    char = guessDB.get_random_character()

    if game_result < 50:
        await update.effective_message.reply_text(
            f"*Oops!* Marriage failed...\n`{to_small_caps(char['name'])}` From Anime `{to_small_caps(char['anime'])}` {random.choice(FAILED)} \n*Better luck next time!*",
            parse_mode="Markdown"
        )
        COOLDOWNS[user.id] = now + timedelta(seconds=random.randint(60, 120))
        return
    else:
        harem_id = userDB.get_harem_id(user.id)
        haremDB.add_waifu_to_harem(harem_id, char['id'])
        stickerf = await update.effective_message.reply_text(f"❤️")
        await asyncio.sleep(1.7)
        await stickerf.delete()
        await asyncio.sleep(1)
        await update.effective_message.reply_photo(
            photo=char['image'],
            caption=f"*{random.choice(NOT_FAILED1)}*\nYᴏᴜ'ʀᴇ *married to* `{to_small_caps(char['name'])}` From Anime `{to_small_caps(char['anime'])}`\n`*{random.choice(NOT_FAILED2)}*`",
            parse_mode="Markdown"
        )
        COOLDOWNS[user.id] = now + timedelta(seconds=random.randint(30, 90))
        