from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from db.coins import coinsDB
from db.rubies import EnhancedRubiesDB
from db.wtokens import wtokensDB
from frequently_used_functions import check_membership
from cmds.start import check_register
import html

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_membership(update, context):
        return
        
    if not await check_register(update, context):
        return

    try:
        if update.message.reply_to_message:
            target_user = update.message.reply_to_message.from_user
        else:
            target_user = update.effective_user
        
        user_id = str(target_user.id)
        
        try:
            coins = coinsDB.get_coins(user_id)
            rubies = EnhancedRubiesDB.get_rubies(user_id)
            wtokens = wtokensDB.get_wtokens(user_id)
        except Exception as e:
            print(f"Error getting balance: {e}")
            await update.message.reply_text("❌ Error retrieving balance data")
            return
        
        # Format user name with HTML link
        if target_user.username:
            user_link = f'<a href="https://t.me/{target_user.username}">{html.escape(target_user.full_name)}</a>'
        else:
            user_link = f"User {html.escape(target_user.full_name)}"
        
        # Create balance message
        balance_msg = (
            f"⚘ ʜᴇʏ, {user_link}! ʜᴇʀᴇ'ꜱ ʏᴏᴜʀ ʙᴀʟᴀɴᴄᴇ ⚘\n\n"
            "    ════════════════════\n"
            f"        ❖  Cᴏɪɴꜱ ➔ {coins:,} ₵\n\n"
            f"       ❖  Rᴜʙɪᴇꜱ ➔ {rubies:,} ✦\n\n"
            f"        ❖  WTᴏKᴇɴꜱ ➔ {wtokens:,} Ⓦ \n"
            "    ════════════════════"
        )
        
        # Try to get profile photo
        photos = await context.bot.get_user_profile_photos(target_user.id, limit=1)
        if photos.photos:
            photo = photos.photos[0][-1]  # Get the largest available photo
            photo_file = await context.bot.get_file(photo.file_id)
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=photo_file.file_id,
                caption=balance_msg,
                parse_mode="HTML"
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=balance_msg,
                parse_mode="HTML"
            )
            
    except Exception as e:
        print(f"Error in balance command: {e}")
        await update.message.reply_text("⚠️ An error occurred while processing your request")