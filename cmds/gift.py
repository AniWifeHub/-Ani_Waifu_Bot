from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from db.users import userDB
from db.guess import guessDB
from db.harem import haremDB
import asyncio
import html
from frequently_used_functions import check_membership
from cmds.start import check_register

async def gift(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await check_membership(update, context):
        return
        
    if not await check_register(update, context):
        return

    if not context.args:
        await update.effective_message.reply_text(
            "Bᴀᴋᴀᴀ!! Enter waifu ID to gift~!"
        )
        return

    if not update.message.reply_to_message:
        await update.effective_message.reply_text(
            "Bᴀᴋᴀᴀ!! Dᴏɴ'ᴛ Fᴏʀɢᴇᴛ ᴛO ʀEᴘLʏ Tᴏ sᴏMᴇᴏNᴇ~!"
        )
        return
    
    user = update.effective_user
    user_harem = userDB.get_harem_id(user.id)
    
    if user_harem is None:
        await update.effective_message.reply_text(
            "Bᴀᴋᴀᴀ!! ʏᴏᴜ ᴅOɴ'ᴛ ʜAᴠᴇ ᴀ ʜᴀRᴇᴍ~!"
        )
        return
    
    waifu_id = context.args[0]
    target_user = update.message.reply_to_message.from_user

    _waifus = guessDB.get_last_id()

    if user.id == target_user.id:
        await update.effective_message.reply_text(
            "Bᴀᴋᴀᴀ!! ᴡʜʏ ᴡᴏᴜʟᴅ ʏᴏᴜ ɢɪғᴛ ᴛᴏ ʏᴏᴜʀsᴇʟғ~?"
        )
        return
    
    if int(waifu_id) > _waifus:
        await update.effective_message.reply_text(
            "Bᴀᴋᴀᴀ!! Tʜᴀᴛ ᴡᴀIғᴜ ɪSɴ'ᴛ Iɴ ᴛHᴇ ɢᴀMᴇ~!"
        )
        return
        
    waifu = guessDB.get_character_with_id(waifu_id)
    
    data = haremDB.load()
    user_harem_id = str(user_harem)
    if user_harem_id not in data['harems'] or waifu_id not in data['harems'][user_harem_id]:
        await update.effective_message.reply_text(
            "Bᴀᴋᴀᴀ!! ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴛʜɪs ᴡᴀɪғᴜ ɪɴ ʏᴏᴜʀ ʜᴀʀᴇᴍ~!"
        )
        return
    
    keyboard = [
        [
            InlineKeyboardButton("Yᴇs", callback_data=f"gift_yes_{waifu_id}_{target_user.id}"),
            InlineKeyboardButton("Nᴏ", callback_data=f"gift_no_{waifu_id}_{target_user.id}")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if target_user.username:
        target_link = f'<a href="https://t.me/{target_user.username}">{html.escape(target_user.full_name)}</a>'
    else:
        target_link = f"User {html.escape(target_user.full_name)}"
        
    # if user.username:
    #     user_link = f'<a href="https://t.me/{user.username}">{html.escape(user.full_name)}</a>'
    # else:
    #     user_link = f"User {html.escape(user.full_name)}"
        
    caption = (
        f"✦ 𝗪𝗮𝗶𝗳𝘂 𝗚𝗶𝗳𝘁 𝗖𝗼𝗻𝗳𝗶𝗿𝗺𝗮𝘁𝗶𝗼𝗻 ✦\n\n"
        f"◈ 𝗡𝗮𝗺𝗲: {waifu['name']}\n"
        f"◈ 𝗔𝗻𝗶𝗺𝗲: {waifu['anime']}\n"
        f"◈ 𝗥𝗮𝗿𝗶𝘁𝘆: {waifu['rarity']}\n\n"
        f"𝗔𝗿𝗲 𝘆𝗼𝘂 𝘀𝘂𝗿𝗲 𝘆𝗼𝘂 𝘄𝗮𝗻𝘁 𝘁𝗼 𝗴𝗶𝗳𝘁 𝘁𝗵𝗶𝘀 𝘄𝗮𝗶𝗳𝘂 𝘁𝗼 {target_link}?"
    )

    confirmation_message = await update.effective_message.reply_photo(
        photo=waifu['image'],
        caption=caption,
        reply_markup=reply_markup
    )
        
    context.user_data['last_gift_message'] = confirmation_message.message_id

async def gift_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    data = query.data.split('_')
    action = data[1]
    waifu_id = data[2]
    target_user_id = int(data[3])
    
    if user.id != update.effective_user.id:
        await query.answer("Bᴀᴋᴀᴀ!! Tʜɪs ɪsɴ'ᴛ ʏᴏᴜʀ Fᴏʀ Yᴏᴜ~!", show_alert=True)
        return
    
    if action == 'no':
        await query.edit_message_text("Gɪғᴛ ᴄᴀɴᴄᴇʟᴇᴅ~!")
        return
    
    user_harem = userDB.get_harem_id(user.id)
    target_harem = userDB.get_harem_id(target_user_id)
    
    if not user_harem or not target_harem:
        await query.edit_message_text("Hᴀʀᴇᴍ ɴᴏᴛ ғᴏᴜɴᴅ~!")
        return
    
    waifu = guessDB.get_character_with_id(waifu_id)
    
    success = haremDB.gift_waifu(user_harem, target_harem, waifu_id)
    
    if success:
        sticker = await query.message.reply_sticker("CAACAgIAAxkBAAIg")
        await asyncio.sleep(1.5)
        await sticker.delete()
        
        await query.edit_message_text(
            f"Yᴏᴜ ɢɪғᴛᴇᴅ {waifu['name']} ᴛᴏ {query.message.reply_to_message.from_user.first_name}~!"
        )
    else:
        await query.edit_message_text("Bᴀᴋᴀᴀ!! Sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ~!")

