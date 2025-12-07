from telegram import Update
from telegram.ext import ContextTypes
import html
from db.users import userDB
from db.coins import coinsDB
from db.rubies import EnhancedRubiesDB
from db.wtokens import wtokensDB
from db.bank import banksDB
from db.harem import haremDB
from db.guess import guessDB
from config import DEFAULT_PROFILE_PHOTO
from frequently_used_functions import check_membership,check_not_private
from cmds.start import check_register
import asyncio

def create_progress_bar(current, total, length=10):
    progress = min(int((current / total) * length), length)
    return "▓" * progress + "░" * (length - progress)

async def get_profile_photo(bot, user_id, default_photo):
    try:
        photos = await bot.get_user_profile_photos(user_id, limit=1)
        if photos.total_count > 0:
            return photos.photos[0][-1].file_id
    except Exception as e:
        print(f"Error getting profile photo: {e}")
    return default_photo

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await check_membership(update, context):
        return
        
    if not await check_register(update, context):
        return
    
    if not await check_not_private(update,context):
        return

    user = update.effective_user
    user_id = user.id
    
    profile_data = {
        'coins': coinsDB.get_coins(user_id),
        'rubies': EnhancedRubiesDB.get_rubies(user_id),
        'wtokens': wtokensDB.get_wtokens(user_id),
        'bank': banksDB.get_bank_balance_with_bank_id(
            userDB.get_bank_id(user_id, user.full_name)
        ),
        'level': userDB.get_user_level(user_id),
        'exp': userDB.get_user_exp(user_id),
        'harem_id': userDB.get_harem_id(user_id)
    }
    
    exp_needed = 1000 * (profile_data['level'] ** 2)
    progress_percent = min(int((profile_data['exp'] / exp_needed) * 100), 100)
    progress_bar = create_progress_bar(profile_data['exp'], exp_needed)
    
    harem_data = haremDB.load().get('harems', {}).get(str(profile_data['harem_id']), {})
    total_waifus = sum(harem_data.values()) if harem_data else 0
    rarity_counts = {rarity: 0 for rarity in ["Godly", "Legendary", "Epic", "Rare", "Uncommon", "Common"]}
    
    for waifu_id, count in harem_data.items():
        char_data = guessDB.get_character_with_id(waifu_id)
        if char_data and char_data.get('rarity') in rarity_counts:
            rarity_counts[char_data['rarity']] += 1
    
    user_link = (f'<a href="https://t.me/{user.username}">{html.escape(user.full_name)}</a>' 
                if user.username else html.escape(user.full_name))
    
    msg = await update.effective_message.reply_text(text="getting your status in database..")
    await asyncio.sleep(0.5)
    await msg.edit_text(text="getting your status in database...")
    await asyncio.sleep(0.8)
    await msg.edit_text(text="getting your status in database.")
    await asyncio.sleep(1)
    await msg.edit_text(text="getting your status in database..")
    await asyncio.sleep(0.5)
    await msg.edit_text(text="getting your status in database...")
    await asyncio.sleep(0.8)
    await msg.edit_text(text="getting your status in database.")
    await asyncio.sleep(1)
    await msg.delete()
    await asyncio.sleep(1)
    
    profile_text = (
        f" Hey, {user_link} sama! here's your status:\n\n"
        f"✦ Level ➝ {profile_data['level']}\n"
        f"   [{progress_bar}] {progress_percent}%\n\n"
        f"💰 Balance Status:\n"
        f"   ⠹ Coins: {profile_data['coins']:,} ₵\n"
        f"   ⠹ Rubies: {profile_data['rubies']:,} ✦\n"
        f"   ⠹ WTokens: {profile_data['wtokens']:,} Ⓦ\n\n"
        f"🏦 Bank Coins: {profile_data['bank']:,}\n\n"
        f"🌸 Harem Status ({total_waifus}/223)\n"
        f"   ✧ Godly: {rarity_counts['Godly']}\n"
        f"   ✧ Legendary: {rarity_counts['Legendary']}\n"
        f"   ✧ Epic: {rarity_counts['Epic']}\n"
        f"   ✧ Rare: {rarity_counts['Rare']}\n"
        f"   ✧ Uncommon: {rarity_counts['Uncommon']}\n"
        f"   ✧ Common: {rarity_counts['Common']}\n\n"
        f"♡ Good luck on your adventures! ♡"
    )
    
    try:
        photo = await get_profile_photo(
            context.bot, 
            user_id, 
            DEFAULT_PROFILE_PHOTO
        )
        
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=photo,
            caption=profile_text,
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Error sending profile: {e}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=profile_text,
            parse_mode="HTML"
        )