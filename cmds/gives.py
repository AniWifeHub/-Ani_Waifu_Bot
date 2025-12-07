from db.coins import coinsDB
from db.wtokens import wtokensDB
from db.rubies import EnhancedRubiesDB
from telegram import Update
from telegram.ext import ContextTypes
import html
from config import OWNER,ADMINS
from db.harem import haremDB
from db.users import userDB
from db.guess import guessDB
import asyncio

async def _cgive_(update: Update,context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    if user.id != OWNER and user.id not in ADMINS:
        await update.message.reply_text("✘ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪꜱꜱɪᴏɴ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ. ✘")
        return

    if not update.message.reply_to_message:
        await update.effective_message.reply_text(
            text=f"Bᴀᴋᴀᴀ!! Dᴏɴ’ᴛ ғᴏʀɢᴇᴛ ᴛᴏ ʀᴇᴘʟʏ ᴛᴏ sᴏᴍᴇᴏɴᴇ~!"
        )
        return
    else:
        target_user = update.message.reply_to_message.from_user

    if not context.args or not context.args[0].isdigit():
        await update.effective_message.reply_text(
            text=f"Bᴀᴋᴀᴀ!! Eɴᴛᴇʀ ᴛʜᴇ ᴀᴍᴏᴜɴᴛ!\n  Exᴀᴍᴘʟᴇ: `/cgive 100`",
            parse_mode='Markdown'
        )
        return
    
    amount = context.args[0]

    user_link = (f'<a href="https://t.me/{target_user.username}">{html.escape(target_user.full_name)}</a>' 
            if target_user.username else html.escape(target_user.full_name))
    
    coinsDB.enhance_coins(target_user.id,amount)

    await update.effective_message.reply_text(text=f"{int(amount):,}Cᴏɪɴs ᴡEʀᴇ SᴜCᴄᴇssғUʟʟʏ ɢIᴠEɴ Tᴏ ᴜSᴇR {user_link}.",parse_mode='HTML')

async def _wgive_(update: Update,context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    if user.id != OWNER and user.id not in ADMINS:
        await update.message.reply_text("✘ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪꜱꜱɪᴏɴ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ. ✘")
        return

    if not update.message.reply_to_message:
        await update.effective_message.reply_text(
            text=f"Bᴀᴋᴀᴀ!! Dᴏɴ’ᴛ ғᴏʀɢᴇᴛ ᴛᴏ ʀᴇᴘʟʏ ᴛᴏ sᴏᴍᴇᴏɴᴇ~!"
        )
        return
    else:
        target_user = update.message.reply_to_message.from_user

    if not context.args or not context.args[0].isdigit():
        await update.effective_message.reply_text(
            text=f"Bᴀᴋᴀᴀ!! Eɴᴛᴇʀ ᴛʜᴇ ᴀᴍᴏᴜɴᴛ!\n  Exᴀᴍᴘʟᴇ: `/wgive 100`",
            parse_mode='Markdown'
        )
        return
    
    amount = context.args[0]

    user_link = (f'<a href="https://t.me/{target_user.username}">{html.escape(target_user.full_name)}</a>' 
            if target_user.username else html.escape(target_user.full_name))
    
    wtokensDB.enhance_wtokens(target_user.id,amount)

    await update.effective_message.reply_text(text=f"{int(amount):,}WTᴏᴋᴇɴs ᴡEʀᴇ SᴜCᴄᴇssғUʟʟʏ ɢIᴠEɴ Tᴏ ᴜSᴇR {user_link}",parse_mode='HTML')


async def _rgive_(update: Update,context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    if user.id != OWNER and user.id not in ADMINS:
        await update.message.reply_text("✘ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪꜱꜱɪᴏɴ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ. ✘")
        return

    if not update.message.reply_to_message:
        await update.effective_message.reply_text(
            text=f"Bᴀᴋᴀᴀ!! Dᴏɴ’ᴛ ғᴏʀɢᴇᴛ ᴛᴏ ʀᴇᴘʟʏ ᴛᴏ sᴏᴍᴇᴏɴᴇ~!"
        )
        return
    else:
        target_user = update.message.reply_to_message.from_user

    if not context.args or not context.args[0].isdigit():
        await update.effective_message.reply_text(
            text=f"Bᴀᴋᴀᴀ!! Eɴᴛᴇʀ ᴛʜᴇ ᴀᴍᴏᴜɴᴛ!\n  Exᴀᴍᴘʟᴇ: `/rgive 100`",
            parse_mode='Markdown'
        )
        return
    
    amount = context.args[0]

    user_link = (f'<a href="https://t.me/{target_user.username}">{html.escape(target_user.full_name)}</a>' 
            if target_user.username else html.escape(target_user.full_name))
    
    EnhancedRubiesDB.update_rubies(target_user.id,amount)

    await update.effective_message.reply_text(text=f"{int(amount):,}Rᴜʙɪᴇs ᴡEʀᴇ SᴜCᴄᴇssғUʟʟʏ ɢIᴠEɴ Tᴏ ᴜSᴇR {user_link}.",parse_mode='HTML')

async def _gwaifu_(update: Update,context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    if user.id != OWNER and user.id not in ADMINS:
        await update.message.reply_text("✘ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪꜱꜱɪᴏɴ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ. ✘")
        return

    if not update.message.reply_to_message:
        await update.effective_message.reply_text(
            text=f"Bᴀᴋᴀᴀ!! Dᴏɴ’ᴛ ғᴏʀɢᴇᴛ ᴛᴏ ʀᴇᴘʟʏ ᴛᴏ sᴏᴍᴇᴏɴᴇ~!"
        )
        return
    else:
        target_user = update.message.reply_to_message.from_user

    if not context.args or not context.args[0].isdigit():
        await update.effective_message.reply_text(
            text=f"Bᴀᴋᴀᴀ!! Eɴᴛᴇʀ ᴛʜᴇ ID!\n  Exᴀᴍᴘʟᴇ: `/gwaifu 1`",
            parse_mode='Markdown'
        )
        return
    
    waifu_id = context.args[0]

    user_link = (f'<a href="https://t.me/{target_user.username}">{html.escape(target_user.full_name)}</a>' 
            if target_user.username else html.escape(target_user.full_name))

    harem_id = userDB.get_harem_id(user.id)
    waifu = guessDB.get_character_with_id(waifu_id)

    haremDB.add_waifu_to_harem(harem_id,waifu_id)

    waifu_name = waifu['name']
    waifu_rarity = waifu['rarity']
    waifu_image = waifu['image']
    waifu_anime = waifu['anime']

    caption = (
        f"<b>ᴏWo~ Yᴏᴜ GɪᴠEᴅ ᴛʜIs CʜAʀᴀᴄTᴇʀ Tᴏ </b> {user_link} <b>sᴀᴍᴀ!</b>,\n\n"
        f"<b>{waifu_id} : {waifu_name}</b>\n"
        f"<b>RᴀʀIᴛʏ({waifu_rarity}) ғRᴏᴍ ᴀNɪMᴇ : {waifu_anime}</b>"
    )
    
    msg = await update.effective_message.reply_text(text=f"GɪᴠIɴɢ..")
    await asyncio.sleep(0.4)
    await msg.edit_text(text=f"GɪᴠIɴɢ...")
    await asyncio.sleep(0.5)
    await msg.edit_text(text=f"GɪᴠIɴɢ.")
    await asyncio.sleep(0.6)
    await msg.edit_text(text=f"GɪᴠIɴɢ..")
    await asyncio.sleep(0.3)
    await msg.edit_text(text=f"GɪᴠIɴɢ...")
    await asyncio.sleep(1)
    await msg.delete()
    await asyncio.sleep(1)

    await update.effective_message.reply_photo(
        photo=waifu_image,
        caption=caption,
        parse_mode="HTML"
    )

async def _cwaifu_(update: Update,context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    if user.id != OWNER and user.id not in ADMINS:
        await update.message.reply_text("✘ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪꜱꜱɪᴏɴ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ. ✘")
        return

    if not update.message.reply_to_message:
        await update.effective_message.reply_text(
            text=f"Bᴀᴋᴀᴀ!! Dᴏɴ’ᴛ ғᴏʀɢᴇᴛ ᴛᴏ ʀᴇᴘʟʏ ᴛᴏ sᴏᴍᴇᴏɴᴇ~!"
        )
        return
    else:
        target_user = update.message.reply_to_message.from_user

    if not context.args or not context.args[0].isdigit():
        await update.effective_message.reply_text(
            text=f"Bᴀᴋᴀᴀ!! Eɴᴛᴇʀ ᴛʜᴇ ID!\n  Exᴀᴍᴘʟᴇ: `/cwaifu 1`",
            parse_mode='Markdown'
        )
        return
    
    waifu_id = context.args[0]

    user_link = (f'<a href="https://t.me/{target_user.username}">{html.escape(target_user.full_name)}</a>' 
            if target_user.username else html.escape(target_user.full_name))

    harem_id = userDB.get_harem_id(user.id)
    waifu = guessDB.get_character_with_id(waifu_id)

    haremDB.remove_waifu_from_harem(harem_id,waifu_id)

    waifu_name = waifu['name']
    waifu_rarity = waifu['rarity']
    waifu_image = waifu['image']
    waifu_anime = waifu['anime']

    caption = (
        f"<b>ᴏWo~ Yᴏᴜ CᴀᴛᴄʜEᴅ ᴛʜIs CʜAʀᴀᴄTᴇʀ From </b> {user_link} <b>sᴀᴍᴀ!</b>,\n\n"
        f"<b>{waifu_id} : {waifu_name}</b>\n"
        f"<b>RᴀʀIᴛʏ({waifu_rarity}) ғRᴏᴍ ᴀNɪMᴇ : {waifu_anime}</b>"
    )
    
    msg = await update.effective_message.reply_text(text=f"CᴀᴛᴄʜIɴɢ..")
    await asyncio.sleep(0.4)
    await msg.edit_text(text=f"CᴀᴛᴄʜIɴɢ...")
    await asyncio.sleep(0.5)
    await msg.edit_text(text=f"CᴀᴛᴄʜIɴɢ.")
    await asyncio.sleep(0.6)
    await msg.edit_text(text=f"CᴀᴛᴄʜIɴɢ..")
    await asyncio.sleep(0.3)
    await msg.edit_text(text=f"CᴀᴛᴄʜIɴɢ...")
    await asyncio.sleep(1)
    await msg.delete()
    await asyncio.sleep(1)

    await update.effective_message.reply_photo(
        photo=waifu_image,
        caption=caption,
        parse_mode="HTML"
    )