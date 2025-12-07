from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import re
from config import OWNER, ADMINS
from db.guess import guessDB

pending_waifus = {}

async def autoaddwaifu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if update.effective_chat.type != "private":
        return

    if user_id != OWNER and user_id not in ADMINS:
        await update.message.reply_text("✘ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪꜱꜱɪᴏɴ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ. ✘")
        return
    
    try:
        count = int(context.args[0]) if context.args else 1
        if count <= 0:
            await update.message.reply_text("✘ ᴘʟᴇᴀꜱᴇ ᴇɴᴛᴇʀ ᴀ ᴘᴏꜱɪᴛɪᴠᴇ ɴᴜᴍʙᴇʀ. ✘")
            return
            
        pending_waifus[user_id] = {
            'count': count,
            'current': 0,
            'waifus': []
        }
        
        await update.message.reply_text(
            f"⟳ ʀᴇᴀᴅʏ ᴛᴏ ᴀᴅᴅ {count} ᴡᴀɪꜰᴜ(ꜱ).\n\n"
            "ᴘʟᴇᴀꜱᴇ ꜱᴇɴᴅ ᴍᴇ ᴛʜᴇ ɪᴍᴀɢᴇꜱ ᴡɪᴛʜ ᴄᴀᴘᴛɪᴏɴꜱ ɪɴ ᴛʜɪꜱ ꜰᴏʀᴍᴀᴛ:\n\n"
            "OwO! Check out this waifu!\n\n"
            "[Anime Name]\n"
            "[ID]: [Character Name]\n"
            "(🟡𝙍𝘼𝙍𝙄𝙏𝙔: Rarity)\n"
        )
        
    except (IndexError, ValueError):
        await update.message.reply_text("ᴜꜱᴀɢᴇ: /autoaddwaifu [number]")

async def handle_waifu_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in pending_waifus or pending_waifus[user_id]['current'] >= pending_waifus[user_id]['count']:
        return
    
    if not update.message.caption:
        await update.message.reply_text("✘ ᴘʟᴇᴀꜱᴇ ɪɴᴄʟᴜᴅᴇ ᴛʜᴇ ʀᴇQᴜɪʀᴇᴅ ᴄᴀᴘᴛɪᴏɴ ᴡɪᴛʜ ᴛʜᴇ ɪᴍᴀɢᴇ. ✘")
        return
    
    caption = update.message.caption
    pattern = (
        r"OwO! Check out this (?:waifu|character)!\n\n"
        r"(.+?)\n"
        r"(\d+): (.+?)\n"
        r"\(.*𝙍𝘼𝙍𝙄𝙏𝙔: (.+?)\)"
    )

    match = re.search(pattern, caption)
    
    if not match:
        await update.message.reply_text("✘ ɪɴᴠᴀʟɪᴅ ᴄᴀᴘᴛɪᴏɴ ꜰᴏʀᴍᴀᴛ. ᴘʟᴇᴀꜱᴇ ᴜꜱᴇ ᴛʜᴇ ᴄᴏʀʀᴇᴄᴛ ꜰᴏʀᴍᴀᴛ. ✘")
        return
    
    anime = match.group(1).strip()
    char_id = match.group(2).strip()
    name = match.group(3).strip()
    rarity = match.group(4).strip()
    photo = update.message.photo[-1].file_id
    
    is_duplicate = False
    for waifu in pending_waifus[user_id]['waifus']:
        if waifu.get('id') == char_id:
            is_duplicate = True
            break
    
    if is_duplicate:
        await update.message.reply_text(
            f"✘ ᴛʜɪꜱ ᴄʜᴀʀᴀᴄᴛᴇʀ (ɪᴅ: {char_id}) ɪꜱ ᴀʟʀᴇᴀᴅʏ ɪɴ ʏᴏᴜʀ ᴘᴇɴᴅɪɴɢ ʟɪꜱᴛ. ✘\n"
            f"ᴘʀᴏɢʀᴇꜱꜱ: {pending_waifus[user_id]['current']}/{pending_waifus[user_id]['count']}",
            parse_mode='HTML'
        )
        return
    
    if guessDB.is_duplicate_character(name, rarity):
        await update.message.reply_text(
            f"✘ ᴄʜᴀʀᴀᴄᴛᴇʀ <b>{name}</b> ᴡɪᴛʜ ʀᴀʀɪᴛʏ <b>{rarity}</b> ᴀʟʀᴇᴀᴅʏ ᴇxɪꜱᴛꜱ ɪɴ ᴛʜᴇ ᴅᴀᴛᴀʙᴀꜱᴇ. ✘\n"
            f"ᴘʀᴏɢʀᴇꜱꜱ: {pending_waifus[user_id]['current']}/{pending_waifus[user_id]['count']}",
            parse_mode='HTML'
        )
        return
    
    pending_waifus[user_id]['waifus'].append({
        'id': char_id,
        'photo': photo,
        'anime': anime,
        'name': name,
        'rarity': rarity
    })
    pending_waifus[user_id]['current'] += 1
    
    remaining = pending_waifus[user_id]['count'] - pending_waifus[user_id]['current']
    
    if remaining > 0:
        await update.message.reply_text(f"✔️ ᴡᴀɪꜰᴜ ᴄᴀᴘᴛᴜʀᴇᴅ ({pending_waifus[user_id]['current']}/{pending_waifus[user_id]['count']}). ꜱᴇɴᴅ {remaining} ᴍᴏʀᴇ.")
    else:
        message = "📝 ᴄᴏɴꜰɪʀᴍ ᴀᴅᴅɪɴɢ ᴛʜᴇꜱᴇ ᴡᴀɪꜰᴜꜱ:\n\n"
        for i, waifu in enumerate(pending_waifus[user_id]['waifus'], 1):
            line = f"{i}. {waifu['name']} ({waifu['rarity']}) - {waifu['anime']} (ɪᴅ: {waifu['id']})"
            
            if len(message) + len(line) + 1 > 1024:
                message += "\n[...ᴛʀᴜɴᴄᴀᴛᴇᴅ...]"
                break
            message += line + "\n"
        
        keyboard = [
            [InlineKeyboardButton("✔️ ᴄᴏɴꜰɪʀᴍ", callback_data="confirm_waifus")],
            [InlineKeyboardButton("✘ ᴄᴀɴᴄᴇʟ", callback_data="cancel_waifus")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=pending_waifus[user_id]['waifus'][0]['photo'],
                caption=message,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        except Exception as e:
            short_message = "📝 ᴄᴏɴꜰɪʀᴍ ᴀᴅᴅɪɴɢ ᴛʜᴇꜱᴇ ᴡᴀɪꜰᴜꜱ? (ᴅᴇᴛᴀɪʟꜱ ᴛᴏᴏ ʟᴏɴɢ ᴛᴏ ᴅɪꜱᴘʟᴀʏ)"
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=pending_waifus[user_id]['waifus'][0]['photo'],
                caption=short_message,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            
async def handle_waifu_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    
    if user_id not in pending_waifus:
        try:
            await query.edit_message_caption(caption="✘ ꜱᴇꜱꜱɪᴏɴ ᴇxᴘɪʀᴇᴅ. ᴘʟᴇᴀꜱᴇ ꜱᴛᴀʀᴛ ᴀɢᴀɪɴ.")
        except:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="✘ ꜱᴇꜱꜱɪᴏɴ ᴇxᴘɪʀᴇᴅ. ᴘʟᴇᴀꜱᴇ ꜱᴛᴀʀᴛ ᴀɢᴀɪɴ."
            )
        return
    
    try:
        if query.data == "confirm_waifus":
            added_count = 0
            for waifu in pending_waifus[user_id]['waifus']:
                try:
                    guessDB.addWaifu(
                        name=waifu['name'],
                        image=waifu['photo'],
                        rarity=waifu['rarity'],
                        anime=waifu['anime']
                    )
                    added_count += 1
                except Exception as e:
                    print(f"Error adding waifu: {e}")
            
            try:
                await query.edit_message_caption(
                    caption=f"✔️ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴀᴅᴅᴇᴅ {added_count} ᴡᴀɪꜰᴜ(ꜱ)!"
                )
            except:
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=f"✔️ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴀᴅᴅᴇᴅ {added_count} ᴡᴀɪꜰᴜ(ꜱ)!"
                )
        else:
            try:
                await query.edit_message_caption(caption="✘ ᴡᴀɪꜰᴜ ᴀᴅᴅɪᴛɪᴏɴ ᴄᴀɴᴄᴇʟᴇᴅ.")
            except:
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text="✘ ᴡᴀɪꜰᴜ ᴀᴅᴅɪᴛɪᴏɴ ᴄᴀɴᴄᴇʟᴇᴅ."
                )
    except Exception as e:
        print(f"Error handling confirmation: {e}")
        try:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="✘ ᴀɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ. ᴘʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ."
            )
        except:
            pass
    
    if user_id in pending_waifus:
        del pending_waifus[user_id]