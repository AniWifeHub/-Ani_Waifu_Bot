from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from db.rewards import rewardsDB
from db.wtokens import wtokensDB
import asyncio
import html
import os
from frequently_used_functions import check_membership
from cmds.start import check_register

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

# Cooldown periods in seconds
DAILY_COOLDOWN = 24 * 60 * 60  # 24 hours
WEEKLY_COOLDOWN = 7 * DAILY_COOLDOWN  # 7 days
MONTHLY_COOLDOWN = 30 * DAILY_COOLDOWN  # 30 days

def format_time_remaining(seconds):
    if seconds <= 0:
        return "Nᴏᴡ"
    
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    components = []
    if days > 0:
        components.append(("Dᴀʏ", days))
    if hours > 0:
        components.append(("HᴏUʀ", hours))
    if minutes > 0:
        components.append(("MɪɴᴜTᴇ", minutes))
    if seconds > 0 or not components:
        components.append(("Sᴇᴄᴏɴᴅ", seconds))
    
    parts = []
    for unit, value in components[:2]:
        value = int(value)
        plural = "s" if value > 1 else ""
        parts.append(f"{value} {unit}{plural}")
    
    return " Aɴᴅ ".join(parts) if len(parts) > 1 else parts[0]

async def check_reward_availability(user_id, reward_type):
    try:
        user_data = rewardsDB.get_user_data(user_id)
        last_claimed = user_data.get(reward_type, 0)
        
        cooldown = {
            "daily": DAILY_COOLDOWN,
            "weekly": WEEKLY_COOLDOWN,
            "monthly": MONTHLY_COOLDOWN
        }.get(reward_type, 0)
        
        if not cooldown:
            return False, "Iɴᴠᴀʟɪᴅ ʀᴇᴡᴀʀᴅ ᴛʏᴘᴇ"
        
        current_time = datetime.now().timestamp()
        elapsed = current_time - last_claimed
        remaining = cooldown - elapsed
        
        return (True, None) if remaining <= 0 else (False, format_time_remaining(remaining))
    except Exception as e:
        print(f"Error in check_reward_availability for user {user_id}: {str(e)}")
        return False, "Eʀʀᴏʀ ᴄʜᴇᴄᴋɪɴɢ ʀᴇᴡᴀʀᴅ ᴀᴠᴀɪʟᴀʙɪʟɪᴛʏ"

def give_reward(reward_type, user_id):
    try:
        rewards = {
            "daily": 130,
            "weekly": 910,
            "monthly": 3640
        }
        amount = rewards.get(reward_type, 50)
        # Ensure user_id is string for consistency
        result = wtokensDB.enhance_wtokens(str(user_id), amount)
        if result is None:
            print(f"Warning: enhance_wtokens returned None for user {user_id}")
            return 0
        return result
    except Exception as e:
        print(f"Error in give_reward for user {user_id}: {str(e)}")
        return 0

async def claim_reward(update, reward_type):
    try:
        user_id = update.effective_user.id
        rewardsDB.update_user_data(user_id, reward_type, datetime.now().timestamp())
        user = update.effective_user
        
        reward_names = {
            "daily": "DᴀɪLʏ",
            "weekly": "WᴇᴇᴋLʏ",
            "monthly": "MᴏɴᴛʜLʏ"
        }
        
        if user.username:
            user_link = f'<a href="https://t.me/{user.username}">{html.escape(user.full_name)}</a>'
        else:
            user_link = html.escape(user.full_name)
        
        reward = give_reward(reward_type, user_id)
        next_reward = format_time_remaining({
            "daily": DAILY_COOLDOWN,
            "weekly": WEEKLY_COOLDOWN,
            "monthly": MONTHLY_COOLDOWN
        }[reward_type])

        sticker = await update.message.reply_sticker("CAACAgIAAyEFAASZnLN9AAIFkGhCmINBj2ylDb5xSC7ecN0p2wu2AAKIDQACu-uhSwmcQT8C1yd4NgQ")
        
        await asyncio.sleep(2)
        await sticker.delete()
        
        return (
            f"🎉 Hᴇʟʟᴏ {user_link}!\n"
            f"✔️ Yᴏᴜ'ᴠᴇ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴄʟᴀɪᴍᴇᴅ ʏᴏᴜʀ {reward_names[reward_type]} ʀᴇᴡᴀʀᴅ!\n\n"
            f" + {reward} Ⓦ\n\n"
            f"⏳ Nᴇxᴛ ʀᴇᴡᴀʀᴅ ɪɴ: {next_reward}"
        )
    except Exception as e:
        print(f"Error in claim_reward for user {update.effective_user.id}: {str(e)}")
        return "🚫 Aɴ ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ ᴄʟᴀɪᴍɪɴɢ ʏᴏᴜʀ ʀᴇᴡᴀʀᴅ. Pʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ."

async def send_reward_message(update, reward_type, available, time_remaining=None):
    try:
        if available:
            message = await claim_reward(update, reward_type)
        else:
            reward_names = {
                "daily": "DᴀɪLʏ",
                "weekly": "WᴇᴇᴋLʏ",
                "monthly": "MᴏɴᴛʜLʏ"
            }
            message = (
                f"⏳ Pʟᴇᴀꜱᴇ ᴡᴀɪᴛ!\n\n"
                f"Yᴏᴜʀ ɴᴇxᴛ {reward_names[reward_type]} ʀᴇᴡᴀʀᴅ ᴡɪʟʟ ʙᴇ ᴀᴠᴀɪʟᴀʙʟᴇ ɪɴ:\n"
                f"🕒 {time_remaining}\n\n"
                f"Pʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ!"
            )
        
        await asyncio.sleep(1)
        
        await update.message.reply_text(
            text=message,
            parse_mode='HTML',
            disable_web_page_preview=True
        )
    except Exception as e:
        print(f"Error in send_reward_message for user {update.effective_user.id}: {str(e)}")
        await update.message.reply_text("🚫 Aɴ �ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ ᴡʜɪʟᴇ ᴘʀᴏᴄᴇꜱꜱɪɴɢ ʏᴏᴜʀ ʀᴇᴡᴀʀᴅ. Pʟᴇᴀꜱᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.")

async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await check_membership(update, context):
        return
        
    if not await check_register(update, context):
        return

    available, time_remaining = await check_reward_availability(update.effective_user.id, "daily")
    await send_reward_message(update, "daily", available, time_remaining)

async def weekly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    if not await check_membership(update, context):
        return
        
    if not await check_register(update, context):
        return

    available, time_remaining = await check_reward_availability(update.effective_user.id, "weekly")
    await send_reward_message(update, "weekly", available, time_remaining)

async def monthly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    if not await check_membership(update, context):
        return
        
    if not await check_register(update, context):
        return

    available, time_remaining = await check_reward_availability(update.effective_user.id, "monthly")
    await send_reward_message(update, "monthly", available, time_remaining)