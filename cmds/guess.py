from db.guess import guessDB
from db.games import gamesDB
from db.harem import haremDB
from db.users import userDB
from db.coins import coinsDB
from telegram import Update
from telegram.ext import ContextTypes
from frequently_used_functions import check_membership,check_not_private
from datetime import datetime
from fuzzywuzzy import fuzz
from cmds.start import check_register

async def guess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    if not await check_membership(update, context):
        return
        
    if not await check_register(update, context):
        return
    
    if not await check_not_private(update,context):
        return
    
    chat_id = update.effective_chat.id

    if gamesDB.check_exist_guess_game(chat_id):
        print("yes")

        game_data = gamesDB.get_guess_game(chat_id)

        char_name = game_data['name']
        char_anime = game_data['anime']
        char_rarity = game_data['rarity']
        char_image = game_data['image']
        char_reward = guessDB.get_reward_with_rarity(char_rarity)
        char_time = datetime.fromisoformat(game_data['start_time'])

        elapsed = (datetime.now() - char_time).total_seconds()
        time_left = max(0,180 - elapsed)

        msg = await update.effective_message.reply_photo(
            photo=char_image,
            caption=f"🌟 𝗢𝘄𝗢! 𝗚𝘂𝗲𝘀𝘀 𝗪𝗵𝗼 𝗜𝘀 𝗧𝗵𝗶𝘀 𝗖𝗵𝗮𝗿𝗮𝗰𝘁𝗲𝗿? 🌟\n\n✦ 𝗥𝗮𝗿𝗶𝘁𝘆: <b>{char_rarity}</b>\n✦ 𝗥𝗲𝘄𝗮𝗿𝗱: {char_reward}ᴄᴏɪɴ\n✦ 𝗧𝗶𝗺𝗲 𝗟𝗲𝗳𝘁: {int(time_left)}ꜱᴇᴄᴏɴᴅꜱ\n\n🔍 𝗥𝗲𝗽𝗹𝘆 𝘄𝗶𝘁𝗵 𝘁𝗵𝗲 𝗖𝗵𝗮𝗿𝗮𝗰𝘁𝗲𝗿'𝘀 𝗡𝗮𝗺𝗲!",
            parse_mode='HTML'
        )

        gamesDB.reload_guess_game_msg_charachter_id(chat_id,msg.id)

    else:
        print("no")
        character = guessDB.get_random_character()
        char_name = character['name']
        char_anime = character['anime']
        char_image = character['image']
        char_rarity = character['rarity']
        char_id = character['id']
        char_reward = guessDB.get_reward_with_rarity(char_rarity)
        print(char_name)

        msg = await update.effective_message.reply_photo(
            photo=char_image,
            caption=f"🌟 𝗢𝘄𝗢! 𝗚𝘂𝗲𝘀𝘀 𝗪𝗵𝗼 𝗜𝘀 𝗧𝗵𝗶𝘀 𝗖𝗵𝗮𝗿𝗮𝗰𝘁𝗲𝗿? 🌟\n\n✦ 𝗥𝗮𝗿𝗶𝘁𝘆: <b>{char_rarity}</b>\n✦ 𝗥𝗲𝘄𝗮𝗿𝗱: {char_reward}ᴄᴏɪɴ\n\n⏳ 𝗬𝗼𝘂 𝗛𝗮𝘃𝗲 𝟯 𝗠𝗶𝗻𝘂𝘁𝗲𝘀!\n🔍 𝗥𝗲𝗽𝗹𝘆 𝘄𝗶𝘁𝗵 𝘁𝗵𝗲 𝗖𝗵𝗮𝗿𝗮𝗰𝘁𝗲𝗿'𝘀 𝗡𝗮𝗺𝗲!",
            parse_mode='HTML'
        )

        job = context.job_queue.run_once(
            callback=end_game,
            when=180,
            chat_id=chat_id,
            data={"chat_id": str(chat_id)},
            name=str(chat_id)
        )
        
        game_data = {
            "name": char_name,
            "image": char_image,
            "rarity": char_rarity,
            "anime": char_anime,
            "msg": msg.id,
            "id": char_id,
            "chat_id": chat_id,
            "start_time": datetime.now().isoformat(),
            "job": job.name,
            "is_active": True
        }
        
        gamesDB.create_guess_game(game_data, chat_id)

async def guess_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message

    if not message.reply_to_message:
        return

    chat_id = str(update.effective_chat.id)
    reply_to_msg_id = message.reply_to_message.message_id

    try:
        if not gamesDB.check_exist_guess_game(chat_id):
            return

        game_data = gamesDB.get_guess_game(chat_id)
        if not game_data:
            return

        if str(reply_to_msg_id) != str(game_data.get('msg')):
            return

        guess = message.text.strip().lower()
        correct_name = game_data.get('name', '').strip().lower()
        
        import re
        correct_name_clean = re.sub(r'[\[\]\🎒✨⚡️]', '', correct_name).strip().lower()
        
        if len(guess) < 3:
            return

        ratio = fuzz.ratio(guess, correct_name_clean)
        token_set = fuzz.token_set_ratio(guess, correct_name_clean)
        
        is_match = (guess in correct_name_clean) or (correct_name_clean in guess)
        
        if is_match or (ratio > 85) or (token_set > 80):
            gamesDB.update_guess_game_status(chat_id, False)
            
            current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
            for job in current_jobs:
                job.schedule_removal()

            user_id = update.effective_user.id
            user_name = update.effective_user.full_name
            harem_id = userDB.get_harem_id(user_id)
            waifu_id = game_data.get('id')
            char_name = game_data.get('name')
            char_anime = game_data.get('anime')
            char_image = game_data.get('image')
            char_rarity = game_data.get('rarity')
            char_reward = guessDB.get_reward_with_rarity(char_rarity) if char_rarity else 0
            
            if waifu_id:
                haremDB.add_waifu_to_harem(harem_id, waifu_id)

            await update.effective_message.reply_photo(
                photo=char_image or "AgACAgQAAxkBAAMzaDoT6i_WdJrJNS9Zw5bDtkUMxE4AAkDJMRvsgNBR5nDtLEqNZE0BAAMCAAN5AAM2BA",
                caption=f"✨ 𝗪𝗲𝗹𝗹 𝗗𝗼𝗻𝗲! 𝗬𝗼𝘂 𝗴𝘂𝗲𝘀𝘀𝗲𝗱 𝗰𝗼𝗿𝗿𝗲𝗰𝘁𝗹𝘆! ✨\n\n✦ 𝗡𝗮𝗺𝗲: {char_name or 'Unknown'}\n✦ 𝗔𝗻𝗶𝗺𝗲: {char_anime or 'Unknown'}\n✦ 𝗥𝗮𝗿𝗶𝘁𝘆: {char_rarity or 'Unknown'}\n\n🎉 𝗬𝗼𝘂 𝗲𝗮𝗿𝗻𝗲𝗱: +{char_reward} 𝗰𝗼𝗶𝗻𝘀\n💖 𝗧𝗵𝗶𝘀 𝗰𝗵𝗮𝗿𝗮𝗰𝘁𝗲𝗿 𝗵𝗮𝘀 𝗯𝗲𝗲𝗻 𝗮𝗱𝗱𝗲𝗱 𝘁𝗼 𝘆𝗼𝘂𝗿 𝗛𝗮𝗿𝗲𝗺!\n\n👉 𝗬𝗼𝘂 𝗰𝗮𝗻 𝘃𝗶𝗲𝘄 𝗶𝘁 𝘂𝘀𝗶𝗻𝗴 /harem",
                parse_mode='HTML'
            )
            
            coinsDB.enhance_coins(user_id,char_reward)
            
            # Remove the game from database
            gamesDB.remove_guess_game(chat_id)
    except Exception as e:
        print(f"Error in guess_reply: {e}")

async def end_game(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.data['chat_id']
    game_data = gamesDB.get_guess_game(chat_id)
    
    if not game_data or not game_data.get('is_active', True):
        return
    
    chat_name = str(abs(int(game_data['chat_id']))).replace("-100", "")
    msg_id = game_data['msg']

    if str(chat_id).startswith('-100'):
        chat_name = str(chat_id).replace('-100', '')

    await context.bot.send_photo(
        chat_id=chat_id,
        photo="AgACAgQAAxkBAAMzaDoT6i_WdJrJNS9Zw5bDtkUMxE4AAkDJMRvsgNBR5nDtLEqNZE0BAAMCAAN5AAM2BA",
        caption=f"⌛️ 𝗧𝗶𝗺𝗲'𝘀 𝗨𝗽!\n⤷ <a href='https://t.me/c/{chat_name}/{msg_id}'>ᴄʜᴀʀᴀᴄᴛᴇʀ</a>\n—————————\n✦ 𝗡𝗮𝗺𝗲: <b>{game_data['name']}</b>\n✦ 𝗔𝗻𝗶𝗺𝗲: <b>{game_data['anime']}</b>\n✦ 𝗥𝗮𝗿𝗶𝘁𝘆: <b>{game_data['rarity']}</b>\n—————————\n✦ 𝗕𝗲𝘁𝘁𝗲𝗿 𝗹𝘂𝗰𝗸 𝗻𝗲𝘅𝘁 𝘁𝗶𝗺𝗲! ✦",
        parse_mode='HTML'
    )
    
    gamesDB.remove_guess_game(chat_id)