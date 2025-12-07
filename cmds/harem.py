from telegram import Update
from telegram.ext import ContextTypes
from db.users import userDB
from db.harem import haremDB
from db.guess import guessDB
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import math
from frequently_used_functions import check_membership
from cmds.start import check_register

ITEMS_PER_PAGE = 5

async def harem(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not await check_membership(update, context):
        return
        
    if not await check_register(update, context):
        return

    user_id = update.effective_user.id
    user_name = update.effective_user.full_name
    
    harem_id = userDB.get_harem_id(user_id)
    harem_data = haremDB.load().get('harems', {}).get(str(harem_id), {})
    characters_data = guessDB.load().get('characters', {})
    
    waifus = []
    unique_waifus = set()
    for waifu_id, count in harem_data.items():
        char_data = characters_data.get(waifu_id, {})
        waifus.append({
            'id': waifu_id,
            'name': char_data.get('name', 'Unknown'),
            'image': char_data.get('image'),
            'rarity': char_data.get('rarity', 'Common'),
            'anime': char_data.get('anime', 'Unknown'),
            'count': count
        })
        unique_waifus.add(waifu_id)
    
    waifus.sort(key=lambda x: int(x['id']), reverse=True)
    
    total_characters = len(unique_waifus)
    total_pages = math.ceil(len(waifus) / ITEMS_PER_PAGE)
    
    await display_collection_page(
        update, context, 
        waifus,
        user_name, 
        page=1, 
        total_pages=total_pages,
        total_characters_count=total_characters
    )

async def display_collection_page(update, context, waifus, user_name, page, total_pages, total_characters_count):
    start_idx = (page - 1) * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    current_waifus = waifus[start_idx:end_idx]
    
    # Build message
    message = f"🗂 Collection of {user_name} - Page 「{page}/{total_pages}」\n\n"
    
    for waifu in current_waifus:
        anime = waifu['anime']
        total_in_anime = sum(1 for char in guessDB.load().get('characters', {}).values() 
                          if char.get('anime') == anime)
        
        message += f":⧽ {anime} 「1/{total_in_anime}」\n"
        
        rarity_sticker = get_rarity_sticker(waifu['rarity'])
        name_parts = waifu['name'].split(' [')
        char_name = name_parts[0]
        emoji = f"[{name_parts[1]}" if len(name_parts) > 1 else ""
        
        message += f"🔘 〔{rarity_sticker}〕 {waifu['id']} {char_name} {emoji} x{waifu['count']}\n\n"
    
    message += f"\n🎉 Total Characters: {total_characters_count}"
    
    keyboard = []
    if page > 1:
        keyboard.append(InlineKeyboardButton("◂ ᴘʀᴇᴠɪᴏᴜꜱ", callback_data=f"collection_page_{page-1}"))
    if page < total_pages:
        keyboard.append(InlineKeyboardButton("ɴᴇxᴛ ▸", callback_data=f"collection_page_{page+1}"))
    
    reply_markup = InlineKeyboardMarkup([keyboard]) if keyboard else None
    
    first_waifu_image = None
    if current_waifus and current_waifus[0].get('image'):
        first_waifu_image = current_waifus[0]['image']
    
    default_image = 'AgACAgQAAxkBAAMzaDoT6i_WdJrJNS9Zw5bDtkUMxE4AAkDJMRvsgNBR5nDtLEqNZE0BAAMCAAN5AAM2BA'
    
    try:
        if 'last_collection_message' in context.user_data:
            try:
                await context.bot.edit_message_caption(
                    chat_id=update.effective_chat.id,
                    message_id=context.user_data['last_collection_message'],
                    caption=message,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
            except Exception as e:
                msg = await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=first_waifu_image or default_image,
                    caption=message,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
                context.user_data['last_collection_message'] = msg.message_id
        else:
            msg = await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=first_waifu_image or default_image,
                caption=message,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
            context.user_data['last_collection_message'] = msg.message_id
    except Exception as e:
        try:
            if 'last_collection_message' in context.user_data:
                await context.bot.edit_message_text(
                    chat_id=update.effective_chat.id,
                    message_id=context.user_data['last_collection_message'],
                    text=message,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
            else:
                msg = await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=message,
                    reply_markup=reply_markup,
                    parse_mode='HTML'
                )
                context.user_data['last_collection_message'] = msg.message_id
        except Exception as e2:
            print(f"Error: {e2}")

async def handle_collection_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    page = int(query.data.split('_')[-1])
    user_id = query.from_user.id
    user_name = query.from_user.full_name
    
    # Reload data
    harem_id = userDB.get_harem_id(user_id)
    harem_data = haremDB.load().get('harems', {}).get(str(harem_id), {})
    characters_data = guessDB.load().get('characters', {})
    
    # Prepare data as flat list
    waifus = []
    unique_waifus = set()
    for waifu_id, count in harem_data.items():
        char_data = characters_data.get(waifu_id, {})
        waifus.append({
            'id': waifu_id,
            'name': char_data.get('name', 'Unknown'),
            'image': char_data.get('image'),
            'rarity': char_data.get('rarity', 'Common'),
            'anime': char_data.get('anime', 'Unknown'),
            'count': count
        })
        unique_waifus.add(waifu_id)
    
    # Sort waifus by ID in descending order (newest first)
    waifus.sort(key=lambda x: int(x['id']), reverse=True)
    
    total_characters = len(unique_waifus)
    total_pages = math.ceil(len(waifus) / ITEMS_PER_PAGE)
    
    await display_collection_page(
        update, context, 
        waifus,
        user_name, 
        page=page, 
        total_pages=total_pages,
        total_characters_count=total_characters
    )

def get_rarity_sticker(rarity):
    stickers = {
        'Common': '🔵',
        'Uncommon': '🟢',
        'Rare': '🔵',
        'Epic': '🟣',
        'Legendary': '🟡',
        'Exclusive': '💮'
    }
    return stickers.get(rarity, '⚪')
