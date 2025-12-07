from telegram import Update
from telegram.ext import ContextTypes
from cmds.start import check_register
from frequently_used_functions import check_membership
from Fonter import to_small_caps
from db.guess import guessDB
import asyncio

async def check_(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not await check_membership(update, context):
        return
        
    if not await check_register(update, context):
        return
    
    if not context.args or len(context.args) == 0:
        await update.effective_message.reply_text(
            text=f"Bᴀᴋᴀᴀ!! Eɴᴛᴇʀ ᴛʜᴇ ID ᴏʀ ɴᴀᴍᴇ!\nExᴀᴍᴘʟᴇ: `/check 85` ᴏʀ `/check Anya`",
            parse_mode='Markdown'
        )
        return
    
    input_arg = context.args[0]
    waifu = None

    # Check if input is a digit (ID)
    if input_arg.isdigit():
        waifu_id = int(input_arg)
        waifu = guessDB.get_character_with_id(waifu_id)
    else:
        # Search by name
        waifu = guessDB.get_character_id_with_name(input_arg)
    
    # Animation while checking
    msg = await update.effective_message.reply_text(to_small_caps(f"? - checking.."))
    await asyncio.sleep(0.7)
    await msg.edit_text(to_small_caps(f"| - checking..."))
    await asyncio.sleep(0.7)
    await msg.edit_text(to_small_caps(f"? - checking."))
    await asyncio.sleep(0.7)
    await msg.edit_text(to_small_caps(f"| - checking.."))
    await asyncio.sleep(1.7)

    if not waifu:
        await update.effective_message.reply_text(to_small_caps(f"This ID/Name doesn't exist in DataBase!"))
        return
    
    rarity_s = guessDB.get_rarity_sticker(waifu['rarity'])
    
    await update.effective_message.reply_photo(
        photo=waifu['image'],
        caption=to_small_caps((
            f"oWo~ Check This Character!\n\n"
            f" *{to_small_caps(str(waifu['id']))} :* `{waifu['name']}`\n"
            f" *Rarity*({to_small_caps(waifu['rarity'])}{rarity_s})\n"
            f"*From Anime:* `{waifu['anime']}`\n\n"
            f"!! Remember This Character :)"
        )),
        parse_mode='Markdown'
    )