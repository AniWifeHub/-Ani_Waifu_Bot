from telegram import Update
from telegram.ext import ContextTypes
from config import OWNER, ADMINS
from db.owner import OwnerC
import re

async def addadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Check if user is owner or admin
    if user.id != OWNER and user.id not in ADMINS:
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return
    
    # Check if replying to a message
    target_user_id = None
    admin_name = None
    
    if update.message.reply_to_message:
        # Get user info from replied message
        target_user = update.message.reply_to_message.from_user
        target_user_id = target_user.id
        admin_name = f"{target_user.first_name}" + (f" {target_user.last_name}" if target_user.last_name else "")
        
        # If additional args provided, use them as custom name
        if context.args:
            admin_name = ' '.join(context.args)
    
    else:
        # Check command format for traditional usage
        if not context.args or len(context.args) < 2:
            await update.message.reply_text(
                "📝 Usage: /addadmin <user_id> <name>\n"
                "       OR reply to a user's message with /addadmin [custom_name]\n\n"
                "Examples:\n"
                "• /addadmin 123456789 John Doe\n"
                "• Reply to user's message: /addadmin Custom Name"
            )
            return
        
        # Extract user_id and name from args
        try:
            target_user_id = int(context.args[0])
            admin_name = ' '.join(context.args[1:])
        except ValueError:
            await update.message.reply_text("❌ Invalid user ID. Please provide a numeric user ID.")
            return
    
    # Validate name
    if len(admin_name) < 2 or len(admin_name) > 50:
        await update.message.reply_text("❌ Name must be between 2 and 50 characters.")
        return
    
    # Add admin to database
    try:
        admin_data = OwnerC.add_admin(OWNER, target_user_id, admin_name)
        
        reply_text = (
            f"✅ **Admin Added Successfully!**\n\n"
            f"👤 **Name:** {admin_data['name']}\n"
            f"🆔 **ID:** `{admin_data['id']}`\n"
            f"📅 **Date:** {admin_data['date']}\n"
            f"👑 **Added by:** {user.first_name}"
        )
        
        # If replying to message, reply to that specific message
        if update.message.reply_to_message:
            await update.message.reply_to_message.reply_text(reply_text)
        else:
            await update.message.reply_text(reply_text)
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error adding admin: {str(e)}")

async def removeadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Check authorization
    if user.id != OWNER and user.id not in ADMINS:
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return
    
    # Check if replying to a message
    target_user_id = None
    
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        target_user_id = target_user.id
    else:
        # Check command format
        if not context.args or len(context.args) != 1:
            await update.message.reply_text(
                "📝 Usage: /removeadmin <user_id>\n"
                "       OR reply to a user's message with /removeadmin\n\n"
                "Examples:\n"
                "• /removeadmin 123456789\n"
                "• Reply to user's message: /removeadmin"
            )
            return
        
        try:
            target_user_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("❌ Invalid user ID. Please provide a numeric user ID.")
            return
    
    try:
        success, message = OwnerC.remove_admin(OWNER, target_user_id)
        
        if success:
            reply_text = (
                f"✅ **Admin Removed Successfully!**\n\n"
                f"🆔 **Removed ID:** `{target_user_id}`\n"
                f"👑 **Removed by:** {user.first_name}"
            )
            
            # If replying to message, reply to that specific message
            if update.message.reply_to_message:
                await update.message.reply_to_message.reply_text(reply_text)
            else:
                await update.message.reply_text(reply_text)
        else:
            await update.message.reply_text(f"❌ {message}")
            
    except Exception as e:
        await update.message.reply_text(f"❌ Error removing admin: {str(e)}")

async def listadmins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Check authorization
    if user.id != OWNER and user.id not in ADMINS:
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return
    
    # Get limit from command if provided
    limit = 20
    if context.args:
        try:
            limit = int(context.args[0])
            limit = min(limit, 50)  # Max limit 50
        except ValueError:
            pass
    
    try:
        admins = OwnerC.list_admins(OWNER, limit)
        
        if not admins:
            await update.message.reply_text("📝 No admins found in the database.")
            return
        
        formatted_list = OwnerC.format_admin_list(admins, f"Admins List (Total: {len(admins)})")
        
        # Split long messages if needed (Telegram has 4096 character limit)
        if len(formatted_list) > 4000:
            # Send in parts
            parts = [formatted_list[i:i+4000] for i in range(0, len(formatted_list), 4000)]
            for part in parts:
                await update.message.reply_text(part)
        else:
            await update.message.reply_text(formatted_list)
            
    except Exception as e:
        await update.message.reply_text(f"❌ Error retrieving admin list: {str(e)}")

async def admininfo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Check authorization
    if user.id != OWNER and user.id not in ADMINS:
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return
    
    # Check if replying to a message
    target_user_id = None
    
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        target_user_id = target_user.id
    else:
        # Check command format
        if not context.args or len(context.args) != 1:
            await update.message.reply_text(
                "📝 Usage: /admininfo <user_id>\n"
                "       OR reply to a user's message with /admininfo\n\n"
                "Examples:\n"
                "• /admininfo 123456789\n"
                "• Reply to user's message: /admininfo"
            )
            return
        
        try:
            target_user_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("❌ Invalid user ID. Please provide a numeric user ID.")
            return
    
    try:
        admin_data = OwnerC.get_admin(OWNER, target_user_id)
        
        if admin_data:
            reply_text = (
                f"👤 **Admin Information**\n\n"
                f"🆔 **ID:** `{admin_data['id']}`\n"
                f"📛 **Name:** {admin_data['name']}\n"
                f"📅 **Added Date:** {admin_data['date']}\n"
                f"👑 **Owner ID:** `{admin_data['owner_id']}`"
            )
            
            # If replying to message, reply to that specific message
            if update.message.reply_to_message:
                await update.message.reply_to_message.reply_text(reply_text)
            else:
                await update.message.reply_text(reply_text)
        else:
            reply_text = "❌ Admin not found."
            if update.message.reply_to_message:
                await update.message.reply_to_message.reply_text(reply_text)
            else:
                await update.message.reply_text(reply_text)
            
    except Exception as e:
        await update.message.reply_text(f"❌ Error retrieving admin info: {str(e)}")

async def isadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Check authorization
    if user.id != OWNER and user.id not in ADMINS:
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return
    
    # Check if replying to a message or has user_id in args
    target_user_id = None
    
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        target_user_id = target_user.id
    elif context.args and len(context.args) == 1:
        try:
            target_user_id = int(context.args[0])
        except ValueError:
            await update.message.reply_text("❌ Invalid user ID. Please provide a numeric user ID.")
            return
    else:
        await update.message.reply_text(
            "📝 Usage: /isadmin <user_id> OR reply to a user's message with /isadmin\n\n"
            "Examples:\n"
            "• /isadmin 123456789\n"
            "• Reply to user's message: /isadmin"
        )
        return
    
    try:
        is_admin = OwnerC.is_admin(OWNER, target_user_id)
        
        if is_admin:
            admin_data = OwnerC.get_admin(OWNER, target_user_id)
            reply_text = (
                f"✅ **This user is an admin!**\n\n"
                f"👤 **Name:** {admin_data['name']}\n"
                f"🆔 **ID:** `{admin_data['id']}`\n"
                f"📅 **Since:** {admin_data['date']}"
            )
        else:
            reply_text = "❌ This user is not an admin."
        
        # If replying to message, reply to that specific message
        if update.message.reply_to_message:
            await update.message.reply_to_message.reply_text(reply_text)
        else:
            await update.message.reply_text(reply_text)
            
    except Exception as e:
        await update.message.reply_text(f"❌ Error checking admin status: {str(e)}")

async def adminstats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Check authorization
    if user.id != OWNER and user.id not in ADMINS:
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return
    
    try:
        stats = OwnerC.get_owner_stats(OWNER)
        
        if stats:
            await update.message.reply_text(
                f"📊 **Admin Statistics**\n\n"
                f"👑 **Owner ID:** `{stats['owner_id']}`\n"
                f"👥 **Total Admins:** {stats['total_admins']}\n"
                f"📅 **Latest Addition:** {stats['latest_addition'] or 'N/A'}"
            )
        else:
            await update.message.reply_text("❌ No data found for this owner.")
            
    except Exception as e:
        await update.message.reply_text(f"❌ Error retrieving statistics: {str(e)}")