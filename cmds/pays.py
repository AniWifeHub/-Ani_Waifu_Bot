import asyncio
from db.coins import coinsDB
from db.rubies import EnhancedRubiesDB
from db.wtokens import wtokensDB
from db.transaction import TransactionDB
from db.users import userDB
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from frequently_used_functions import check_membership
from cmds.start import check_register

user_cooldowns = {}

def check_cooldown(user_id: int, cooldown_seconds: int = 300) -> bool:
    now = datetime.now()
    last_used = user_cooldowns.get(user_id)
    
    if last_used and (now - last_used) < timedelta(seconds=cooldown_seconds):
        return True
    return False

async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await check_membership(update, context):
        return
        
    if not await check_register(update, context):
        return

    user_id = update.effective_user.id
    
    if check_cooldown(user_id):
        remaining = (user_cooldowns[user_id] + timedelta(minutes=5) - datetime.now()).seconds
        await update.effective_message.reply_text(
            text=f"⏳ Bᴀᴋᴀᴀ!! Yᴏᴜ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪɴ {remaining} sᴇᴄᴏɴᴅs!"
        )
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
            text=f"Bᴀᴋᴀᴀ!! Eɴᴛᴇʀ ᴛʜᴇ ᴀᴍᴏᴜɴᴛ!\n  Exᴀᴍᴘʟᴇ: `/pay 100`",
            parse_mode='Markdown'
        )
        return
    
    amount = context.args[0]
    user_balance = coinsDB.get_coins(user_id)
    if str(amount) is "*":
        amount = user_balance
    else:
        amount = int(amount)

    if amount <= 0:
        await update.effective_message.reply_text(
            text=f"Bᴀᴋᴀᴀ!! Tʜᴇ ᴀᴍᴏᴜɴᴛ ᴍᴜsᴛ ʙᴇ ɢʀᴇᴀᴛᴇʀ ᴛʜᴀɴ 0!"
        )
        return
    
    if amount > user_balance:
        await update.effective_message.reply_text(
            text=f"Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴇɴᴏᴜɢʜ ʙᴀʟᴀɴᴄᴇ!"
        )
        return
    
    if target_user.id == user_id:
        await update.effective_message.reply_text(
            text=f"Bᴀᴋᴀᴀ!! Yᴏᴜ ᴄᴀɴ'ᴛ ᴘᴀʏ ᴍᴏɴᴇʏ ᴛᴏ ʏᴏᴜʀsᴇʟғ!"
        )
        return
    
    if not userDB.exist_user(target_user.id):
        await update.effective_message.reply_text(
            f"Bᴀᴋᴀᴀ!! Tʜᴇ ᴛᴀʀɢᴇᴛ ᴜsᴇʀ ɪs ɴᴏᴛ ʀᴇɢɪsᴛᴇʀᴇᴅ ɪɴ ᴛʜᴇ ᴅᴀᴛᴀʙᴀsᴇ!"
        )
        return

    coinsDB.enhance_coins(target_user.id, amount)
    coinsDB.reduce_coins(user_id, amount)

    processing_msg = await update.effective_message.reply_text(text=f"🔁 Sᴇɴᴅɪɴɢ {amount:,} Cᴏɪɴꜱ ᴛᴏ {target_user.full_name}...")
    await asyncio.sleep(1.5)
    await processing_msg.edit_text(f"🔃 Sᴇɴᴅɪɴɢ {amount:,} Cᴏɪɴꜱ ᴛᴏ {target_user.full_name}...")
    await asyncio.sleep(1.5)
    await processing_msg.edit_text(f"🔁 Sᴇɴᴅɪɴɢ {amount:,} Cᴏɪɴꜱ ᴛᴏ {target_user.full_name}...")
    await asyncio.sleep(3)

    user_name = update.effective_user.full_name or update.effective_user.username or user_id
    target_name = target_user.full_name or target_user.username or target_user.id
    tx_id = TransactionDB.add_transaction(user_id, "paying", amount)
    user_balance = coinsDB.get_coins(user_id)
    target_balance = coinsDB.get_coins(target_user.id)

    await processing_msg.edit_text(
        f"✔️ Tʀᴀɴsғᴇʀ sᴜᴄᴄᴇssғᴜʟ!\n\n"
        f"▸ ꜰʀᴏᴍ {user_name}\n"
        f"▸ ᴛᴏ {target_name}\n"
        f"▸ ᴀᴍᴏᴜɴᴛ: {amount:,} Cᴏɪɴꜱ\n"
        f"▸ ᴛʀᴀɴꜱᴀᴄᴛɪᴏɴ ɪᴅ: `{tx_id}`\n"
        f"▸ ᴅᴀᴛᴇ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"💰 ʏᴏᴜʀ ɴᴇᴡ ʙᴀʟᴀɴᴄᴇ: {user_balance:,}\n"
        f"💰 {target_name} ɴᴇᴡ ʙᴀʟᴀɴᴄᴇ: {target_balance:,}",
        parse_mode='Markdown'
    )

    user_cooldowns[user_id] = datetime.now()

async def pay_wtokens(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await check_membership(update, context):
        return
        
    if not await check_register(update, context):
        return

    user_id = update.effective_user.id
    
    if check_cooldown(user_id):
        remaining = (user_cooldowns[user_id] + timedelta(minutes=5) - datetime.now()).seconds
        await update.effective_message.reply_text(
            text=f"⏳ Bᴀᴋᴀᴀ!! Yᴏᴜ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪɴ {remaining} sᴇᴄᴏɴᴅs!"
        )
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
            text=f"Bᴀᴋᴀᴀ!! Eɴᴛᴇʀ ᴛʜᴇ ᴀᴍᴏᴜɴᴛ!\n  Exᴀᴍᴘʟᴇ: `/pay 100`",
            parse_mode='Markdown'
        )
        return
    
    amount = context.args[0]
    user_balance = wtokensDB.get_wtokens(user_id)
    if str(amount) == "*":
        amount = user_balance
    else:
        amount = int(amount)

    if amount <= 0:
        await update.effective_message.reply_text(
            text=f"Bᴀᴋᴀᴀ!! Tʜᴇ ᴀᴍᴏᴜɴᴛ ᴍᴜsᴛ ʙᴇ ɢʀᴇᴀᴛᴇʀ ᴛʜᴀɴ 0!"
        )
        return
    
    if amount > user_balance:
        await update.effective_message.reply_text(
            text=f"Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴇɴᴏᴜɢʜ WTᴏKᴇɴꜱ!"
        )
        return
    
    if target_user.id == user_id:
        await update.effective_message.reply_text(
            text=f"Bᴀᴋᴀᴀ!! Yᴏᴜ ᴄᴀɴ'ᴛ sᴇɴᴅ WTᴏKᴇɴꜱ ᴛᴏ ʏᴏᴜʀsᴇʟғ!"
        )
        return
    
    if not userDB.exist_user(target_user.id):
        await update.effective_message.reply_text(
            f"Bᴀᴋᴀᴀ!! Tʜᴇ ᴛᴀʀɢᴇᴛ ᴜsᴇʀ ɪs ɴᴏᴛ ʀᴇɢɪsᴛᴇʀᴇᴅ ɪɴ ᴛʜᴇ ᴅᴀᴛᴀʙᴀsᴇ!"
        )
        return
    
    wtokensDB.enhance_wtokens(target_user.id, amount)
    wtokensDB.reduce_wtokens(user_id, amount)

    processing_msg = await update.effective_message.reply_text(text=f"🔁 Sᴇɴᴅɪɴɢ {amount:,} WTᴏKᴇɴꜱ ᴛᴏ {target_user.full_name}...")
    await asyncio.sleep(1.5)
    await processing_msg.edit_text(f"🔃 Sᴇɴᴅɪɴɢ {amount:,} WTᴏKᴇɴꜱ ᴛᴏ {target_user.full_name}...")
    await asyncio.sleep(1.5)
    await processing_msg.edit_text(f"🔁 Sᴇɴᴅɪɴɢ {amount:,} WTᴏKᴇɴꜱ ᴛᴏ {target_user.full_name}...")
    await asyncio.sleep(3)

    user_name = update.effective_user.full_name or update.effective_user.username or user_id
    target_name = target_user.full_name or target_user.username or target_user.id
    tx_id = TransactionDB.add_transaction(user_id, "paying_wtokens", amount)
    user_balance = wtokensDB.get_wtokens(user_id)
    target_balance = wtokensDB.get_wtokens(target_user.id)

    await processing_msg.edit_text(
        f"✔️ Sᴇɴᴅ sᴜᴄᴄᴇssғᴜʟ!\n\n"
        f"▸ ꜰʀᴏᴍ {user_name}\n"
        f"▸ ᴛᴏ {target_name}\n"
        f"▸ ᴀᴍᴏᴜɴᴛ: {amount:,} WTᴏKᴇɴꜱ\n"
        f"▸ ᴛʀᴀɴꜱᴀᴄᴛɪᴏɴ ɪᴅ: `{tx_id}`\n"
        f"▸ ᴅᴀᴛᴇ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"💰 ʏᴏᴜʀ ɴᴇᴡ ʙᴀʟᴀɴᴄᴇ: {user_balance:,}\n"
        f"💰 {target_name} ɴᴇᴡ ʙᴀʟᴀɴᴄᴇ: {target_balance:,}",
        parse_mode='Markdown'
    )

    user_cooldowns[user_id] = datetime.now()

async def pay_ruby(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if check_cooldown(user_id):
        remaining = (user_cooldowns[user_id] + timedelta(minutes=5) - datetime.now()).seconds
        await update.effective_message.reply_text(
            text=f"⏳ Bᴀᴋᴀᴀ!! Yᴏᴜ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪɴ {remaining} sᴇᴄᴏɴᴅs!"
        )
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
            text=f"Bᴀᴋᴀᴀ!! Eɴᴛᴇʀ ᴛʜᴇ ᴀᴍᴏᴜɴᴛ!\n  Exᴀᴍᴘʟᴇ: `/pay 100`",
            parse_mode='Markdown'
        )
        return
    
    amount = context.args[0]
    user_balance = EnhancedRubiesDB.get_rubies(user_id)
    if str(amount) == "*":
        amount = user_balance
    else:
        amount = int(amount)

    if amount <= 0:
        await update.effective_message.reply_text(
            text=f"Bᴀᴋᴀᴀ!! Tʜᴇ ᴀᴍᴏᴜɴᴛ ᴍᴜsᴛ ʙᴇ ɢʀᴇᴀᴛᴇʀ ᴛʜᴀɴ 0!"
        )
        return
    
    if amount > user_balance:
        await update.effective_message.reply_text(
            text=f"Yᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴇɴᴏᴜɢʜ Rᴜʙɪᴇꜱ!"
        )
        return
    
    if target_user.id == user_id:
        await update.effective_message.reply_text(
            text=f"Bᴀᴋᴀᴀ!! Yᴏᴜ ᴄᴀɴ'ᴛ sᴇɴᴅ Rᴜʙɪᴇꜱ ᴛᴏ ʏᴏᴜʀsᴇʟғ!"
        )
        return
    
    if not userDB.exist_user(target_user.id):
        await update.effective_message.reply_text(
            f"Bᴀᴋᴀᴀ!! Tʜᴇ ᴛᴀʀɢᴇᴛ ᴜsᴇʀ ɪs ɴᴏᴛ ʀᴇɢɪsᴛᴇʀᴇᴅ ɪɴ ᴛʜᴇ ᴅᴀᴛᴀʙᴀsᴇ!"
        )
        return

    EnhancedRubiesDB.update_rubies(target_user.id, amount)
    EnhancedRubiesDB.update_rubies(user_id, -amount)

    processing_msg = await update.effective_message.reply_text(text=f"🔁 Sᴇɴᴅɪɴɢ {amount:,} Rᴜʙɪᴇꜱ ᴛᴏ {target_user.full_name}...")
    await asyncio.sleep(1.5)
    await processing_msg.edit_text(f"🔃 Sᴇɴᴅɪɴɢ {amount:,} Rᴜʙɪᴇꜱ ᴛᴏ {target_user.full_name}...")
    await asyncio.sleep(1.5)
    await processing_msg.edit_text(f"🔁 Sᴇɴᴅɪɴɢ {amount:,} Rᴜʙɪᴇꜱ ᴛᴏ {target_user.full_name}...")
    await asyncio.sleep(3)

    user_name = update.effective_user.full_name or update.effective_user.username or user_id
    target_name = target_user.full_name or target_user.username or target_user.id
    tx_id = TransactionDB.add_transaction(user_id, "paying_ruby", amount)
    user_balance = EnhancedRubiesDB.get_rubies(user_id)
    target_balance = EnhancedRubiesDB.get_rubies(target_user.id)

    await processing_msg.edit_text(
        f"✔️ Sᴇɴᴅ sᴜᴄᴄᴇssғᴜʟ!\n\n"
        f"▸ ꜰʀᴏᴍ {user_name}\n"
        f"▸ ᴛᴏ {target_name}\n"
        f"▸ ᴀᴍᴏᴜɴᴛ: {amount:,} Rᴜʙɪᴇꜱ\n"
        f"▸ ᴛʀᴀɴꜱᴀᴄᴛɪᴏɴ ɪᴅ: `{tx_id}`\n"
        f"▸ ᴅᴀᴛᴇ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"💰 ʏᴏᴜʀ ɴᴇᴡ ʙᴀʟᴀɴᴄᴇ: {user_balance:,}\n"
        f"💰 {target_name} ɴᴇᴡ ʙᴀʟᴀɴᴄᴇ: {target_balance:,}",
        parse_mode='Markdown'
    )

    user_cooldowns[user_id] = datetime.now()