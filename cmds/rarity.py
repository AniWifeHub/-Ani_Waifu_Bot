from telegram import Update
from telegram.ext import ContextTypes
from db.guess import guessDB
from config import OWNER , ADMINS

async def rarity_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if update.effective_chat.type != "private":
        return
    
    if user_id != OWNER and user_id not in ADMINS:
        await update.message.reply_text("✘ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪꜱꜱɪᴏɴ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.")
        return
    
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("✘ ᴜꜱᴀɢᴇ: /rarity add <rarity_name> <reward_value>")
        return
    
    try:
        rarity_name = ' '.join(context.args[:-1])
        reward_value = int(context.args[-1])
        
        if reward_value <= 0:
            await update.message.reply_text("✘ ʀᴇᴡᴀʀᴅ ᴠᴀʟᴜᴇ ᴍᴜꜱᴛ ʙᴇ ᴀ ᴘᴏꜱɪᴛɪᴠᴇ ɴᴜᴍʙᴇʀ.")
            return
            
        result = guessDB.add_rarity_reward(rarity_name, reward_value)
        if result:
            await update.message.reply_text(f"✔️ ᴀᴅᴅᴇᴅ ɴᴇᴡ ʀᴀʀɪᴛʏ ʀᴇᴡᴀʀᴅ:\n{rarity_name}: {reward_value}")
        else:
            await update.message.reply_text(f"✘ ʀᴀʀɪᴛʏ '{rarity_name}' ᴀʟʀᴇᴀᴅʏ ᴇxɪꜱᴛꜱ. ᴜꜱᴇ /ʀᴀʀɪᴛʏ ᴇᴅɪᴛ ᴛᴏ ᴄʜᴀɴɢᴇ ɪᴛꜱ ᴠᴀʟᴜᴇ.")
            
    except ValueError:
        await update.message.reply_text("✘ ʀᴇᴡᴀʀᴅ ᴠᴀʟᴜᴇ ᴍᴜꜱᴛ ʙᴇ ᴀ ɴᴜᴍʙᴇʀ.")

async def rarity_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if update.effective_chat.type != "private":
        return
    
    if user_id != OWNER and user_id not in ADMINS:
        await update.message.reply_text("✘ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪꜱꜱɪᴏɴ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ. ✘")
        return
    
    if not context.args or len(context.args) < 2:
        await update.message.reply_text("✘ ᴜꜱᴀɢᴇ: /rarity edit <rarity_name> <new_reward_value>")
        return
    
    try:
        rarity_name = ' '.join(context.args[:-1])
        new_reward = int(context.args[-1])
        
        if new_reward <= 0:
            await update.message.reply_text("✘ ʀᴇᴡᴀʀᴅ ᴠᴀʟᴜᴇ ᴍᴜꜱᴛ ʙᴇ ᴀ ᴘᴏꜱɪᴛɪᴠᴇ ɴᴜᴍʙᴇʀ.")
            return
            
        result = guessDB.change_rarity_reward(rarity_name, new_reward)
        if result:
            await update.message.reply_text(f"✔️ ᴜᴘᴅᴀᴛᴇᴅ ʀᴀʀɪᴛʏ ʀᴇᴡᴀʀᴅ:\n{rarity_name}: {new_reward}")
        else:
            await update.message.reply_text(f"✘ ʀᴀʀɪᴛʏ '{rarity_name}'ɴᴏᴛ ꜰᴏᴜɴᴅ. ᴜꜱᴇ /rarityadd ᴛᴏ ᴄʀᴇᴀᴛᴇ ɪᴛ.")
            
    except ValueError:
        await update.message.reply_text("✘ ʀᴇᴡᴀʀᴅ ᴠᴀʟᴜᴇ ᴍᴜꜱᴛ ʙᴇ ᴀ ɴᴜᴍʙᴇʀ.")

async def rarity_list(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_chat.type != "private":
        return

    rewards = guessDB.rarity_rewards()
    
    if not rewards:
        await update.message.reply_text("🛈 ɴᴏ ʀᴀʀɪᴛʏ ʀᴇᴡᴀʀᴅꜱ ʜᴀᴠᴇ ʙᴇᴇɴ ꜱᴇᴛ ʏᴇᴛ.")
        return
    
    message = "📋 ʀᴀʀɪᴛʏ ʀᴇᴡᴀʀᴅꜱ ʟɪꜱᴛ:\n\n"
    for rarity, reward in rewards:
        message += f"• {rarity}: {reward}\n"
    
    await update.message.reply_text(message)
