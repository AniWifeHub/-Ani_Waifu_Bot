import json
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup,InputMediaPhoto
from telegram.ext import ContextTypes
from db.guess import guessDB
from db.users import userDB
from db.coins import coinsDB
from db.harem import haremDB
import time
from datetime import timedelta

stores = 'data/stores.json'

class StoreDB:
    @staticmethod
    def load():
        try:
            with open(stores, 'r', encoding='utf-8') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    @staticmethod
    def save(data):
        with open(stores, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)

    @staticmethod
    def user_exists(user_id):
        """Check if user has store data"""
        data = StoreDB.load()
        return str(user_id) in data

    @staticmethod
    def generate_random_characters(count=3, guaranteed_rarity=None):
        """
        Generate random characters for store
        Optional: guarantee at least one character of specified rarity
        """
        characters = []
        for _ in range(count):
            char = guessDB.get_random_character()
            characters.append(char)
        
        # Add guaranteed rarity if specified and not already present
        if guaranteed_rarity:
            has_rarity = any(c['rarity'] == guaranteed_rarity for c in characters)
            if not has_rarity:
                # Get a character with specified rarity
                all_chars = guessDB.load().get('characters', {}).values()
                rarity_chars = [c for c in all_chars if c.get('rarity') == guaranteed_rarity]
                if rarity_chars:
                    characters[-1] = random.choice(rarity_chars)
        
        return characters

    @staticmethod
    def init_user_store(user_id):
        """Initialize store for new user"""
        data = StoreDB.load()
        if str(user_id) not in data:
            # New users get one guaranteed Rare or better character
            data[str(user_id)] = {
                'characters': StoreDB.generate_random_characters(guaranteed_rarity="Rare"),
                'refresh_count': 0,
                'last_refresh': None,
                'daily_reset': int(time.time()) + 86400  # 24 hours from now
            }
            StoreDB.save(data)
            return True
        return False

    @staticmethod
    def get_user_store(user_id):
        """Get user's store data with auto-initialization"""
        StoreDB.init_user_store(user_id)
        data = StoreDB.load()
        store_data = data.get(str(user_id))
        
        # Check for daily reset
        if store_data and 'daily_reset' in store_data:
            if time.time() > store_data['daily_reset']:
                store_data['refresh_count'] = 0
                store_data['daily_reset'] = int(time.time()) + 86400
                StoreDB.save(data)
        
        return store_data

    @staticmethod
    def refresh_store(user_id):
        """Refresh store items"""
        data = StoreDB.load()
        user_id = str(user_id)
        if user_id in data:
            store_data = data[user_id]
            
            # Premium users get one guaranteed Epic or better
            is_premium = userDB.is_premium(user_id)
            guaranteed_rarity = "Epic" if is_premium else None
            
            store_data['characters'] = StoreDB.generate_random_characters(
                guaranteed_rarity=guaranteed_rarity
            )
            store_data['refresh_count'] += 1
            store_data['last_refresh'] = int(time.time())
            StoreDB.save(data)
            return True
        return False

    @staticmethod
    def buy_character(user_id, char_index):
        """Purchase character from store"""
        data = StoreDB.load()
        user_id = str(user_id)
        if user_id in data and char_index < len(data[user_id]['characters']):
            character = data[user_id]['characters'][char_index]
            
            # Remove purchased character from store
            data[user_id]['characters'].pop(char_index)
            
            # Add a new random character to keep store full
            if len(data[user_id]['characters']) < 3:
                data[user_id]['characters'].append(guessDB.get_random_character())
            
            StoreDB.save(data)
            return character
        return None

async def store(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Display the character store with pagination"""
    user = update.effective_user
    store_data = StoreDB.get_user_store(user.id)
    
    if not store_data:
        await update.message.reply_text("❌ Error loading store!")
        return
    
    # Get current page from context or default to 0
    page = context.user_data.get('store_page', 0)
    characters = store_data['characters']
    
    # Paginate characters (1 per page)
    total_pages = len(characters)
    if page >= total_pages:
        page = 0
        context.user_data['store_page'] = 0
    
    if not characters:
        await update.message.reply_text("🛒 The store is currently empty!")
        return
    
    character = characters[page]
    refresh_count = store_data.get('refresh_count', 0)
    
    # Calculate price with discount
    price = calculate_price(character['rarity'])
    discount = userDB.get_discount(user.id) if userDB.is_premium(user.id) else 0
    final_price = int(price * (1 - discount/100))
    
    # Create message with character details
    message = (
        f"🛒 *Character Store* (Page {page+1}/{total_pages})\n\n"
        f"🎭 *{character['name']}*\n"
        f"📺 Anime: {character['anime']}\n"
        f"✨ Rarity: {character['rarity']}\n"
        f"💰 Price: ~~{price:,}~~ {final_price:,} coins ({discount}% off)\n\n"
    )
    
    # Create keyboard buttons
    keyboard = []
    
    # Navigation buttons
    nav_buttons = []
    if total_pages > 1:
        nav_buttons.append(
            InlineKeyboardButton("⬅️ Previous", callback_data=f"store_prev_{page}")
        )
        nav_buttons.append(
            InlineKeyboardButton("➡️ Next", callback_data=f"store_next_{page}")
        )
        keyboard.append(nav_buttons)
    
    # Action buttons
    action_buttons = [
        InlineKeyboardButton(
            f"Buy ({final_price:,}₵)", 
            callback_data=f"buy_{page}"
        )
    ]
    keyboard.append(action_buttons)
    
    # Refresh button if available
    max_refreshes = 5 if userDB.is_premium(user.id) else 3
    if refresh_count < max_refreshes:
        refresh_cost = calculate_refresh_cost(refresh_count)
        keyboard.append([
            InlineKeyboardButton(
                f"🔁 Refresh Store ({refresh_cost}₵)", 
                callback_data="refresh_store"
            )
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Try to send character image with caption
    try:
        if 'image' in character:
            await context.bot.send_photo(
                chat_id=update.effective_chat.id,
                photo=character['image'],
                caption=message,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                message,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
    except Exception as e:
        print(f"Error sending store item: {e}")
        await update.message.reply_text(
            "⚠️ Couldn't load character image. Showing details instead...",
            parse_mode="Markdown"
        )
        await update.message.reply_text(
            message,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

async def handle_store_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all store interactions with pagination"""
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    data = query.data
    
    # Helper function to safely update store message
    async def update_store_message():
        store_data = StoreDB.get_user_store(user.id)
        page = context.user_data.get('store_page', 0)
        characters = store_data['characters']
        character = characters[page]
        
        # Calculate price with discount
        price = calculate_price(character['rarity'])
        discount = userDB.get_discount(user.id) if userDB.is_premium(user.id) else 0
        final_price = int(price * (1 - discount/100))
        
        # Create message with character details
        message = (
            f"🛒 *Character Store* (Page {page+1}/{len(characters)})\n\n"
            f"🎭 *{character['name']}*\n"
            f"📺 Anime: {character['anime']}\n"
            f"✨ Rarity: {character['rarity']}\n"
            f"💰 Price: ~~{price:,}~~ {final_price:,} coins ({discount}% off)\n\n"
        )
        
        # Create keyboard buttons
        keyboard = []
        
        # Navigation buttons
        nav_buttons = []
        if len(characters) > 1:
            nav_buttons.append(
                InlineKeyboardButton("⬅️ Previous", callback_data=f"store_prev_{page}")
            )
            nav_buttons.append(
                InlineKeyboardButton("➡️ Next", callback_data=f"store_next_{page}")
            )
            keyboard.append(nav_buttons)
        
        # Action buttons
        action_buttons = [
            InlineKeyboardButton(
                f"Buy ({final_price:,}₵)", 
                callback_data=f"buy_{page}"
            )
        ]
        keyboard.append(action_buttons)
        
        # Refresh button if available
        refresh_count = store_data.get('refresh_count', 0)
        max_refreshes = 5 if userDB.is_premium(user.id) else 3
        if refresh_count < max_refreshes:
            refresh_cost = calculate_refresh_cost(refresh_count)
            keyboard.append([
                InlineKeyboardButton(
                    f"🔁 Refresh Store ({refresh_cost}₵)", 
                    callback_data="refresh_store"
                )
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        try:
            # Try to edit message with photo
            if 'image' in character:
                try:
                    await query.message.edit_media(
                        InputMediaPhoto(
                            media=character['image'],
                            caption=message,
                            parse_mode="Markdown"
                        ),
                        reply_markup=reply_markup
                    )
                    return
                except:
                    pass
            
            # Fallback to text message
            await query.edit_message_text(
                message,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Error updating store message: {e}")
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=message,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
    
    # Handle navigation
    if data.startswith("store_prev_"):
        page = int(data.split("_")[2])
        context.user_data['store_page'] = max(0, page-1)
        await update_store_message()
        return
    
    elif data.startswith("store_next_"):
        page = int(data.split("_")[2])
        store_data = StoreDB.get_user_store(user.id)
        total_pages = len(store_data['characters'])
        context.user_data['store_page'] = min(page+1, total_pages-1)
        await update_store_message()
        return
    
    # Handle refresh
    elif data == "refresh_store":
        store_data = StoreDB.get_user_store(user.id)
        refresh_count = store_data.get('refresh_count', 0)
        max_refreshes = 5 if userDB.is_premium(user.id) else 3
        
        if refresh_count >= max_refreshes:
            await query.answer("❌ You've used all your daily refreshes!", show_alert=True)
            return
        
        refresh_cost = calculate_refresh_cost(refresh_count)
        
        if coinsDB.get_coins(user.id) < refresh_cost:
            await query.answer(f"❌ You need {refresh_cost} coins to refresh!", show_alert=True)
            return
        
        coinsDB.reduce_coins(user.id, refresh_cost)
        StoreDB.refresh_store(user.id)
        context.user_data['store_page'] = 0
        await update_store_message()
        await query.answer("🔄 Store refreshed!")
        return
    
    # Handle purchase
    elif data.startswith("buy_"):
        char_index = int(data.split("_")[1])
        character = StoreDB.buy_character(user.id, char_index)
        
        if not character:
            await query.answer("❌ Character not available!", show_alert=True)
            return
        
        price = calculate_price(character['rarity'])
        discount = userDB.get_discount(user.id) if userDB.is_premium(user.id) else 0
        final_price = int(price * (1 - discount/100))
        
        if coinsDB.get_coins(user.id) < final_price:
            await query.answer(f"❌ You need {final_price} coins to buy this!", show_alert=True)
            return
        
        coinsDB.reduce_coins(user.id, final_price)
        harem_id = userDB.get_harem_id(user.id, user.full_name)
        haremDB.add_waifu_to_harem(harem_id, character['id'])
        
        # Show purchase confirmation as alert
        confirmation_msg = (
            f"✅ Purchased {character['name']}!\n"
            f"💰 Paid: {final_price:,} coins\n"
            f"✨ Rarity: {character['rarity']}\n"
            f"Added to your harem."
        )
        await query.answer(confirmation_msg, show_alert=True)
        
        # Update the store view
        await update_store_message()
               
def calculate_price(rarity):
    """Calculate price based on rarity with scaling"""
    base_prices = {
        "Common": 1000,
        "Uncommon": 2500,
        "Rare": 5000,
        "Epic": 10000,
        "Legendary": 25000,
        "Godly": 50000
    }
    return base_prices.get(rarity, 1000)

def calculate_refresh_cost(refresh_count):
    """Calculate refresh cost with increasing price"""
    base_cost = 500
    return base_cost * (refresh_count + 1)