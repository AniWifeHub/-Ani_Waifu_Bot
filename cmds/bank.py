import asyncio
import html
from datetime import datetime
from db.bank import banksDB
from db.users import userDB
from db.coins import coinsDB
from db.transaction import TransactionDB
from telegram import Update
from telegram.ext import ContextTypes
from frequently_used_functions import check_membership
from cmds.start import check_register

async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await check_membership(update, context):
        return
        
    if not await check_register(update, context):
        return

    user = update.effective_user

    if not context.args or len(context.args) < 1:
        await update.effective_message.reply_text(f"Usᴀɢᴇ: `/deposit <amount>`", parse_mode='Markdown')
        return
    
    amount = context.args[0]

    user_bank = userDB.get_bank_id(user.id, user.full_name)
    user_coins = coinsDB.get_coins(user.id)

    if amount == "*":
        amount = user_coins
    else:
        try:
            amount = int(amount)
        except ValueError:
            await update.effective_message.reply_text("Bᴀᴋᴀᴀ!! ᴇɴᴛᴇʀ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ ᴏʀ Use `/deposit *` ᴛᴏ ᴅᴇᴘᴏsɪᴛ ᴀʟʟ ᴄᴏɪɴs.",parse_mode='Markdown')
            return

    if amount == 0:
        await update.effective_message.reply_text(f"Bᴀᴋᴀᴀ!! Tʜᴇ ᴠᴀʟᴜᴇ ᴄᴀɴɴᴏᴛ ʙᴇ 0!")
        return
    
    if amount > user_coins:
        await update.effective_message.reply_text(f"Bᴀᴋᴀᴀ!! Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ Eɴᴏᴜɢʜ ᴄᴏɪɴs!")
        return
    
    sticker = await update.effective_message.reply_sticker("CAACAgIAAxkBAAIEkGhCfAABYsO3Al2sFRTDkzrmF78vOAAC8QEAAladvQohKm5i6iYv7jYE")
    await asyncio.sleep(3)
    await sticker.delete()

    banksDB.save_bank(user_bank, amount)
    coinsDB.reduce_coins(user.id,amount)
    tx = TransactionDB.add_transaction(user.id, "deposit_bank", amount)
    user_bank_balance = banksDB.get_bank_balance_with_bank_id(user_bank)

    await update.effective_message.reply_photo(
        photo="AgACAgQAAxkBAAIEk2hCfoaO3CTiNt3IZvG7U5rshIfjAAI7zDEbPrIRUoRQ4zFtf_mwAQADAgADeAADNgQ",
        caption=(
            f"✔️ DᴇᴘᴏSɪᴛ sᴜᴄᴄᴇssғᴜʟ!\n\n"
            f"▸ AᴍᴏᴜNᴛ: {amount:,} Cᴏɪɴꜱ\n"
            f"▸ TʀᴀɴꜱᴀᴛIᴏɴ ɪᴅ: `{tx}`\n"
            f"▸ DᴀTᴇ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"💰 YᴏUʀ ɴEᴡ ʙAɴᴋ ʙAʟᴀCᴇ: `{user_bank_balance:,}`\n"
        ),
        parse_mode='Markdown'
    )

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not context.args or len(context.args) < 1:
        await update.effective_message.reply_text(f"Usᴀɢᴇ: `/withdraw <amount>`", parse_mode='Markdown')
        return
    
    amount = context.args[0]

    user_bank = userDB.get_bank_id(user.id, user.full_name)
    user_bank_balance = banksDB.get_bank_balance_with_bank_id(user_bank)

    if amount == "*":
        amount = user_bank_balance
    else:
        try:
            amount = int(amount)
        except ValueError:
            await update.effective_message.reply_text("Bᴀᴋᴀᴀ!! ᴇɴᴛᴇʀ ᴀ ᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ ᴏʀ Use `/withdraw *` ᴛᴏ ᴡɪᴛʜᴅʀᴀᴡ ᴀʟʟ ᴄᴏɪɴs.",parse_mode='Markdown')
            return

    if amount == 0:
        await update.effective_message.reply_text(f"Bᴀᴋᴀᴀ!! Tʜᴇ ᴠᴀʟᴜᴇ ᴄᴀɴɴᴏᴛ ʙᴇ 0!")
        return
    
    if amount > user_bank_balance:
        await update.effective_message.reply_text(f"Bᴀᴋᴀᴀ!! Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ Eɴᴏᴜɢʜ ᴄᴏɪɴs ɪɴ ʏᴏᴜʀ ʙᴀɴᴋ!")
        return
    
    sticker = await update.effective_message.reply_sticker("CAACAgIAAxkBAAIEkGhCfAABYsO3Al2sFRTDkzrmF78vOAAC8QEAAladvQohKm5i6iYv7jYE")
    await asyncio.sleep(3)
    await sticker.delete()

    banksDB.withdraw_bank(user_bank, amount)
    coinsDB.enhance_coins(user.id, amount)
    tx = TransactionDB.add_transaction(user.id, "withdraw_bank", amount)
    new_bank_balance = banksDB.get_bank_balance_with_bank_id(user_bank)

    await update.effective_message.reply_photo(
        photo="AgACAgQAAxkBAAIElmhCgHo5VvWZQve9igjSNjZ9VzNlAAI9zDEbPrIRUhHNohbGAmIVAQADAgADeQADNgQ",
        caption=(
            f"✔️ Wɪᴛʜᴅʀᴀᴡ sᴜᴄᴄᴇssғᴜʟ!\n\n"
            f"▸ AᴍᴏᴜNᴛ: {amount:,} Cᴏɪɴꜱ\n"
            f"▸ TʀᴀɴꜱᴀᴛIᴏɴ ɪᴅ: `{tx}`\n"
            f"▸ DᴀTᴇ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"💰 YᴏUʀ ɴEᴡ ʙAʟᴀCᴇ: `{new_bank_balance:,}`\n"
        ),
        parse_mode='Markdown'
    )

async def bank(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_bank = userDB.get_bank_id(user.id, user.username)
    user_bank_balance = banksDB.get_bank_balance_with_bank_id(user_bank)

    sticker = await update.effective_message.reply_sticker("CAACAgIAAyEFAASZnLN9AAIFemhCh9N21IGgllRWG0sUIWWHOC6nAAIDAQACVp29CgLl0XiH5fpPNgQ")
    await asyncio.sleep(3)
    await sticker.delete()

    if user.username:
        user_link = f'<a href="https://t.me/{user.username}">{html.escape(user.full_name)}</a>'
    else:
        user_link = html.escape(user.full_name)
    
    msg=(
        f"🏦 Hᴇʏ {user_link}, Hᴇʀᴇ'ꜱ Yᴏᴜʀ ʙAɴᴋ ᴀᴄᴄᴏUɴᴛ:\n\n"
        f"• BᴀNᴋ ɪᴅ: <code>{user_bank}</code>\n"
        f"• BᴀʟᴀɴCᴇ: <code>{user_bank_balance:,}</code>\n\n"
        f"DᴀTᴇ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    photos = await context.bot.get_user_profile_photos(user.id, limit=1)
    if photos.photos:
        photo = photos.photos[0][-1]
        photo_file = await context.bot.get_file(photo.file_id)
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo_file.file_id,
            caption=msg,
            parse_mode="HTML"
        )
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=msg,
            parse_mode="HTML"
        )