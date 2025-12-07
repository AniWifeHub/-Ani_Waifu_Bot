from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import OWNER, ADMINS, MAIN_CHANNEL_ID as MCI, MAIN_GROUP_ID as MGI, MAIN_CHANNEL_NAME, MAIN_GROUP_NAME

async def check_channel_membership(bot, user_id):
    if user_id == OWNER:
        return True
    
    if user_id in ADMINS:
        return True
    
    member = await bot.get_chat_member(chat_id=MCI, user_id=user_id)
    return member.status in ["member", "administrator", "creator"]

async def check_group_membership(bot, user_id):
    if user_id == OWNER:
        return True
    
    if user_id in ADMINS:
        return True
    
    member = await bot.get_chat_member(chat_id=MGI, user_id=user_id)
    return member.status in ["member", "administrator", "creator"]

async def check_membership(update, context):
    user = update.effective_user
    user_id = user.id
    user_fullname = user.full_name
    user_name = user.username

    channel_key_markup = InlineKeyboardButton(text="ᴍᴀɪɴ ᴄʜᴀɴɴᴇʟ", url=f"https://t.me/{MAIN_CHANNEL_NAME}")
    group_key_markup = InlineKeyboardButton(text="ᴍᴀɪɴ ɢʀᴏᴜᴘ", url=f"https://t.me/{MAIN_GROUP_NAME}")
    
    is_channel_member = await check_channel_membership(context.bot, user_id)
    is_group_member = await check_group_membership(context.bot, user_id)
    
    if not is_channel_member and not is_group_member:
        markup_keys = InlineKeyboardMarkup([[channel_key_markup, group_key_markup]])
    elif not is_channel_member:
        markup_keys = InlineKeyboardMarkup([[channel_key_markup]])
    elif not is_group_member:
        markup_keys = InlineKeyboardMarkup([[group_key_markup]])
    else:
        return True

    await update.effective_message.reply_photo(
        photo="AgACAgQAAxkBAAMqaDnbZSubSA7MaqDD55czCKvTaTwAAqXMMRsES8hRvWUE333GaFgBAAMCAAN5AAM2BA",
        caption=f'<b>❖ ᴜꜱᴇʀ {user_fullname} ᴛᴏ ᴜꜱᴇ ᴛʜᴇ ʙᴏᴛ, ʏᴏᴜ ᴍᴜꜱᴛ ʙᴇ ᴀ ᴍᴇᴍʙᴇʀ ᴏꜰ ᴛʜᴇ ꜰᴏʟʟᴏᴡɪɴɢ ᴄʜᴀᴛꜱ. ❖</b>',
        reply_markup=markup_keys,
        parse_mode='HTML'
    )
    return False

async def check_not_private(update, context) -> bool:
    if update.effective_chat.type == "private":
        group_key_markup = InlineKeyboardButton(
            text="ᴍᴀɪɴ ɢʀᴏᴜᴘ", 
            url=f"https://t.me/{MAIN_GROUP_NAME}"
        )
        markup_key = InlineKeyboardMarkup([[group_key_markup]])
        
        await update.message.reply_photo(
            photo="AgACAgQAAxkBAAMmaDna3FV36xl8aR7PehmTVr55gGsAAhXGMRsfm9BRC6TiXQciYI8BAAMCAAN4AAM2BA",
            caption=(
                '<b>✘ ʏᴏᴜ ᴄᴀɴɴᴏᴛ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ɪɴ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ. ✘</b>\n\n'
                '<b>✧ ꜱᴜɢɢᴇꜱᴛᴇᴅ ᴄʜᴀᴛ: ✧</b>'
            ),
            reply_markup=markup_key,
            parse_mode='HTML'
        )
        return False
    return True

