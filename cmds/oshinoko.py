import random
import asyncio
import html
from datetime import datetime, timedelta
from typing import Dict
from db.rubies import EnhancedRubiesDB
from db.oshinoko import EnhancedOshinokoDB
from config import OWNER,ADMINS
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import ContextTypes
from frequently_used_functions import check_membership
from cmds.start import check_register

COOLDOWNS: Dict[int, datetime] = {}
MIN_CONCERT_COST = 250
WIN_PROBABILITY = 0.4

CUSTOM_WIN_TEXTS = [
    "🌟 Tʜᴇ sTᴀɢE ʙʟEᴡ Uᴘ ᴡIᴛʜ ᴀPᴘʟAᴜSᴇ! 🔥",
    "🎉 AᴜᴅɪᴇNᴄᴇ ᴡEɴᴛ ᴄʀᴀZʏ! 🔊",
    "📸 CᴀᴍEʀᴀs ᴄᴀN'ᴛ sᴛOᴘ FɪʟᴍIɴɢ ʏOᴜ! 🎥",
    "✨ YᴏU sᴛᴏLᴇ ᴛHᴇ SᴘOᴛʟIɢʜᴛ! 🌟",
    "🌐 Tʜᴇ ɪɴTᴇʀɴEᴛ Is ʙRᴇᴀᴋIɴɢ ᴏVᴇR ʏOᴜʀ PᴇʀғOʀᴍᴀɴCᴇ! 💻🔥"
]

CUSTOM_LOSE_TEXTS = [
    "💔 Tʜᴇ ᴍIᴄ ᴄᴜᴛ ᴏUᴛ... TᴏUɢʜ ʟUᴄᴋ! 🎙️",
    "😶 TʜE ᴀᴜᴅIᴇɴCᴇ SᴛᴀYᴇᴅ sIʟᴇNᴛ...",
    "😢 Aɴ ᴀWᴋᴡᴀRᴅ ᴘᴀUsᴇ sᴛOʟᴇ ᴛHᴇ ᴍᴏMᴇɴᴛ.",
    "💔 YᴏU ɢᴀVᴇ YᴏUʀ ʙEsᴛ, ʙUᴛ ɴOᴛ EɴᴏUɢʜ ᴛOᴅᴀʏ.",
    "⏳ SᴏMᴇ ᴅRᴇᴀᴍS ɴEᴇᴅ ᴍᴏRᴇ ᴛIᴍE."
]

async def concert(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    if not await check_membership(update, context):
        return
        
    if not await check_register(update, context):
        return

    user = update.effective_user
    args = context.args
    now = datetime.now()

    # Check cooldown
    if user.id in COOLDOWNS and COOLDOWNS[user.id] > now:
        remaining = COOLDOWNS[user.id] - now
        minutes, seconds = divmod(int(remaining.total_seconds()), 60)
        await update.message.reply_text(
            f"⏳ Yᴏᴜ ᴀʀᴇ ᴏɴ ᴄᴏᴏʟᴅᴏᴡɴ! Tʀʏ ᴀɢᴀɪɴ ɪɴ {minutes}m {seconds}s."
        )
        return

    # Determine ruby amount
    try:
        if not args:
            ruby_amount = int(EnhancedRubiesDB.get_rubies(user.id) * 0.35)
        elif args[0] == '*':
            ruby_amount = EnhancedRubiesDB.get_rubies(user.id)
        else:
            ruby_amount = int(args[0])
    except (ValueError, IndexError):
        await update.message.reply_text(
            "❌ Iɴᴠᴀʟɪᴅ ᴀᴍᴏᴜɴᴛ. Usᴇ `/concert`, `/concert *` ᴏʀ `/concert [ᴀᴍᴏᴜɴᴛ]`."
        )
        return

    # Validate amount
    if ruby_amount < MIN_CONCERT_COST:
        await update.message.reply_text(
            f"❌ Yᴏᴜ ɴᴇᴇᴅ ᴀᴛ ʟᴇᴀsᴛ {MIN_CONCERT_COST} ʀᴜʙʏ ᴛᴏ sᴛᴀʀᴛ ᴀ ᴄᴏɴᴄᴇʀᴛ."
        )
        return

    user_idol = EnhancedOshinokoDB.get_idol(user.id)
    if not user_idol:
        await update.message.reply_text("💡 Sᴇʟᴇᴄᴛ ᴀɴ ɪᴅᴏʟ ғɪʀsᴛ ᴜsɪɴɢ /startonk ᴏʀ /idol.")
        return

    win_vid = EnhancedOshinokoDB.get_video(user_idol, is_win=True)
    lose_vid = EnhancedOshinokoDB.get_video(user_idol, is_win=False)
    if not win_vid or not lose_vid:
        await update.message.reply_text("⚠️ Nᴏ ᴠɪᴅᴇᴏs sᴇᴛ ғᴏʀ ᴛʜɪs ɪᴅᴏʟ!")
        return

    if EnhancedRubiesDB.get_rubies(user.id) < ruby_amount:
        await update.message.reply_text("❌ Nᴏᴛ ᴇɴᴏᴜɢʜ ʀᴜʙʏ ᴛᴏ sᴛᴀʀᴛ ᴛʜᴇ ᴄᴏɴᴄᴇʀᴛ.")
        return

    msg = await update.message.reply_text(f"🎤 Sᴛᴀʀᴛɪɴɢ ᴄᴏɴᴄᴇʀᴛ ᴡɪᴛʜ {ruby_amount} ʀᴜʙʏ..")
    await asyncio.sleep(1.5)
    await msg.edit_text(f"🎤 Sᴛᴀʀᴛɪɴɢ ᴄᴏɴᴄᴇʀᴛ ᴡɪᴛʜ {ruby_amount} ʀᴜʙʏ...")
    await asyncio.sleep(1.5)
    await msg.edit_text(f"🎤 Sᴛᴀʀᴛɪɴɢ ᴄᴏɴᴄᴇʀᴛ ᴡɪᴛʜ {ruby_amount} ʀᴜʙʏ.")
    await asyncio.sleep(1.5)
    await msg.edit_text(f"🎤 Sᴛᴀʀᴛɪɴɢ ᴄᴏɴᴄᴇʀᴛ ᴡɪᴛʜ {ruby_amount} ʀᴜʙʏ..")
    await asyncio.sleep(1)
    await msg.delete()
    await asyncio.sleep(1)

    mic_msg = await update.message.reply_text("🎤")
    await asyncio.sleep(0.5)
    await mic_msg.edit_text("💫")
    await asyncio.sleep(0.5)
    await mic_msg.edit_text("🌟")
    await asyncio.sleep(1.5)
    await mic_msg.delete()

    user_name = None

    if user.username:
        user_name = f'<a href="https://t.me/{user.username}">{html.escape(user.full_name)}</a>'
    else:
        user_name = f"User {html.escape(user.full_name)}"

    if random.random() <= WIN_PROBABILITY:
        percent_gain = random.randint(34, 69)
        win_amount = int(ruby_amount * (1 + percent_gain / 100))
        EnhancedRubiesDB.update_rubies(user.id, win_amount)
        
        caption = (
            f"ʜᴇʏ, {user_name} ꜱᴀᴍᴀ! 🌟 Cᴏɴᴄᴇʀᴛ ᴡᴀs ᴀ ʜɪᴛ!\n\n"
            f"🎉 Yᴏᴜ ᴇᴀʀɴᴇᴅ {win_amount:,} ʀᴜʙʏ! (+{percent_gain}%)\n\n"
            f"{random.choice(CUSTOM_WIN_TEXTS)}"
        )
        await update.message.reply_video(
            video=win_vid,
            caption=caption,
            parse_mode='HTML'
        )
        COOLDOWNS[user.id] = now + timedelta(seconds=random.randint(90, 180))
    else:
        # Lose scenario
        refund_percent = random.randint(25, 55)
        returned = int(ruby_amount * (refund_percent / 100))
        EnhancedRubiesDB.update_rubies(user.id, -(ruby_amount - returned))
        
        caption = (
            f"ʜᴇʏ, {user_name} ꜱᴀᴍᴀ! 💔 Tʜᴇ sᴛᴀɢᴇ ᴡᴀs ʀᴏᴜɢʜ.\n\n"
            f"Yᴏᴜ ʟᴏsᴛ {ruby_amount - returned:,} ʀᴜʙʏ, ʙᴜᴛ ʀᴇᴄᴏᴠᴇʀᴇᴅ {returned:,}.\n\n"
            f"{random.choice(CUSTOM_LOSE_TEXTS)}"
        )
        await update.message.reply_video(
            video=lose_vid,
            caption=caption,
            parse_mode='HTML'
        )
        COOLDOWNS[user.id] = now + timedelta(seconds=random.randint(120, 360))

async def idol(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle idol selection with interactive buttons"""
    user = update.effective_user
    current_idol = EnhancedOshinokoDB.get_idol(user.id)

    text = (
        f"Yᴏᴜʀ ᴄᴜʀʀᴇɴᴛ ɪᴅᴏʟ: {current_idol}\nCʜᴏᴏsᴇ ᴀ ɪᴅᴏʟ:" 
        if current_idol else 
        "Cʜᴏᴏsᴇ ʏᴏᴜʀ ɪᴅᴏʟ:"
    )

    keyboard = [
        [InlineKeyboardButton("AI Hoshino", callback_data="idol_ai")],
        [InlineKeyboardButton("Ruby Hoshino", callback_data="idol_ruby")],
        [InlineKeyboardButton("MEM-cho", callback_data="idol_memcho")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        photos = await context.bot.get_user_profile_photos(user.id)
        if photos.total_count > 0:
            photo_file_id = photos.photos[0][0].file_id
            await update.message.reply_photo(
                photo=photo_file_id,
                caption=text,
                reply_markup=reply_markup
            )
            return
    except Exception:
        pass

    await update.message.reply_text(text, reply_markup=reply_markup)

async def idol_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    original_msg = query.message.reply_to_message
    
    if original_msg and user.id != original_msg.from_user.id:
        await query.answer("🚫 Tʜɪs ɪs ɴᴏᴛ ғᴏʀ ʏᴏᴜ!", show_alert=True)
        return

    idol_choice = query.data.split("_")[1]
    idol_map = {
        "ai": "AI Hoshino",
        "ruby": "Ruby Hoshino",
        "memcho": "MEM-cho"
    }

    if selected_idol := idol_map.get(idol_choice):
        EnhancedOshinokoDB.set_idol(user.id, selected_idol)
        
        try:
            await query.message.delete()
        except Exception as e:
            print(f"Error deleting message: {e}")
        
        # Send new reply message
        response = f"✨ {selected_idol} ʜᴀs ʙᴇᴇɴ sᴇʟᴇᴄᴛᴇᴅ!"
        
        # Try to reply to the original message if it exists
        if original_msg:
            await original_msg.reply_text(response)
        else:
            # Fallback to sending to the same chat
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=response
            )
    else:
        await query.edit_message_text(text="❌ Eʀʀᴏʀ ɪɴ sᴇʟᴇᴄᴛɪɴɢ ɪᴅᴏʟ.")

async def setvid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    user = await update.effective_user

    if user.id != OWNER and user.id not in ADMINS:
        await update.message.reply_text("✘ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪꜱꜱɪᴏɴ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ. ✘")
        return

    if not update.message.reply_to_message or not update.message.reply_to_message.video:
        await update.message.reply_text(
            "❌ Pʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴠɪᴅᴇᴏ ᴡɪᴛʜ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ!"
        )
        return

    try:
        if len(context.args) < 2:
            raise ValueError("invalid_format")
        
        idol_name = context.args[0].lower()
        result_type = context.args[1].lower()
        
        valid_idols = ["ai", "ruby", "mem-cho"]
        if idol_name not in valid_idols:
            raise ValueError("invalid_idol")
            
        if result_type not in ["win", "lose"]:
            raise ValueError("invalid_type")
            
    except (IndexError, ValueError) as e:
        error_msg = {
            "invalid_idol": "❌ Iɴᴠᴀʟɪᴅ ɪᴅᴏʟ! Usᴇ: ai/ruby/mem-cho",
            "invalid_type": "❌ Iɴᴠᴀʟɪᴅ ᴛʏᴘᴇ! Usᴇ: win/lose",
            "invalid_format": "❌ Iɴᴠᴀʟɪᴅ ғᴏʀᴍᴀᴛ!\nUsᴇ: /setvid [ai/ruby/mem-cho] [win/lose]"
        }.get(str(e), "❌ Iɴᴠᴀʟɪᴅ ɪɴᴘᴜᴛ!")
        
        await update.message.reply_text(error_msg)
        return

    idol_map = {
        "ai": "AI Hoshino",
        "ruby": "Ruby Hoshino",
        "mem-cho": "MEM-cho"
    }
    full_idol_name = idol_map[idol_name]
    video_id = update.message.reply_to_message.video.file_id
    
    data = EnhancedOshinokoDB._load_data()
    
    if "gifs" not in data:
        data["gifs"] = {}
    if full_idol_name not in data["gifs"]:
        data["gifs"][full_idol_name] = {"wingif": [], "losegif": []}
    
    key = "wingif" if result_type == "win" else "losegif"
    if video_id not in data["gifs"][full_idol_name][key]:
        data["gifs"][full_idol_name][key].append(video_id)
        EnhancedOshinokoDB._save_data(data)
        
        win_count = len(data["gifs"][full_idol_name]["wingif"])
        lose_count = len(data["gifs"][full_idol_name]["losegif"])
        
        await update.message.reply_text(
            f"✅ Vɪᴅᴇᴏ ᴀᴅᴅᴇᴅ ғᴏʀ {full_idol_name}'s {result_type} ʀᴇsᴜʟᴛs!\n"
            f"📊 Tᴏᴛᴀʟ ᴡɪɴ ᴠɪᴅᴇᴏs: {win_count}\n"
            f"📊 Tᴏᴛᴀʟ ʟᴏsᴇ ᴠɪᴅᴇᴏs: {lose_count}"
        )
    else:
        await update.message.reply_text(
            "⚠️ Tʜɪs ᴠɪᴅᴇᴏ ɪs ᴀʟʀᴇᴀᴅʏ sᴇᴛ ғᴏʀ ᴛʜɪs ɪᴅᴏʟ!"
        )