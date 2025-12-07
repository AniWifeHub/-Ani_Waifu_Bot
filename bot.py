from telegram import Update,BotCommand
from telegram.ext import Application,ApplicationBuilder,CommandHandler,ContextTypes,JobQueue,MessageHandler,filters,CallbackQueryHandler,ConversationHandler
from config import BOT_TOKEN
from cmds.start import start
from cmds.guess import guess, guess_reply
from cmds.harem import harem, handle_collection_pagination
from cmds.auto_add_waifu import autoaddwaifu, handle_waifu_photo, handle_waifu_confirmation
from cmds.rarity import rarity_add, rarity_edit, rarity_list
from cmds.sticker import rarity_sticker_add, rarity_sticker_edit,rarity_sticker_list
from cmds.balance import balance_command
from cmds.oshinoko import concert,idol,idol_callback,setvid
from cmds.pays import pay,pay_ruby,pay_wtokens
from cmds.bank import deposit,withdraw,bank
from cmds.rewards import daily,weekly,monthly
from cmds.gift import gift_confirmation,gift
from cmds.status import status
from cmds.store import store,handle_store_callback
from cmds.gives import _cgive_,_rgive_,_wgive_,_gwaifu_,_cwaifu_
from cmds.marry import marry
from cmds.check import check_
from cmds.cheat import name,add_bypass,remove_bypass,clear_bypass
from cmds.count import count
from cmds.owner import addadmin, removeadmin, listadmins, admininfo, isadmin, adminstats
import psutil
import platform
from datetime import datetime

async def gpid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return

    if not update.message.reply_to_message.photo:
        return

    replied_photo = update.message.reply_to_message.photo[-1]
    file_id = replied_photo.file_id
    print(file_id)
    await update.effective_message.reply_text(text=file_id)

async def gsid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message and update.message.reply_to_message.sticker:
        sticker = update.message.reply_to_message.sticker
        file_id = sticker.file_id
        print(file_id)
        await update.effective_message.reply_text(text=file_id)
    else:
        return
    
async def set_bot_commands(application: Application):
    commands = [
        BotCommand("guess", "Starting the character guessing game"),
        BotCommand("harem", "Show your harem"),
        BotCommand("marry", "A romantic opportunity to find a new spouse!"),
        BotCommand("bal", "View balance"),
        BotCommand("pay", "Transfer coins to another user"),
        BotCommand("check", "Checking a character")
    ]
    await application.bot.set_my_commands(commands)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).job_queue(JobQueue()).post_init(set_bot_commands).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status",status))
    app.add_handler(CommandHandler("guess", guess))
    app.add_handler(CommandHandler("name", name))
    app.add_handler(CommandHandler("marry",marry))
    # app.add_handler(CommandHandler("store",store))
    app.add_handler(CommandHandler("harem", harem))
    # app.add_handler(CommandHandler("tops",))
    # app.add_handler(CommandHandler("gift",gift))
    # app.add_handler(CommandHandler("gtops",))
    # app.add_handler(CommandHandler("rarity",))
    app.add_handler(CommandHandler("check",check_))
    app.add_handler(CommandHandler("count",count))
    app.add_handler(CommandHandler("startonk",idol))
    app.add_handler(CommandHandler("concert",concert))
    app.add_handler(CommandHandler("idol", idol))
    app.add_handler(CommandHandler("pay",pay))
    app.add_handler(CommandHandler("rpay",pay_ruby))
    app.add_handler(CommandHandler("wpay",pay_wtokens))
    app.add_handler(CommandHandler(["balance", "bal"], balance_command))
    app.add_handler(CommandHandler("deposit", deposit))
    app.add_handler(CommandHandler("withdraw",withdraw))
    app.add_handler(CommandHandler("bank",bank))
    app.add_handler(CommandHandler("daily",daily))
    app.add_handler(CommandHandler("weekly",weekly))
    app.add_handler(CommandHandler("monthly",monthly))
    # app.add_handler(CommandHandler("fight",fight))
    # app.add_handler(CommandHandler("leave",leave))
    # app.add_handler(CommandHandler("hunt",hunt))
    # app.add_handler(CommandHandler("inventory",inventory))
    # app.add_handler(CommandHandler("weapons",weapons))
    # app.add_handler(CommandHandler("use",use))
    # app.add_handler(CommandHandler("cosino",cosino))


# CAACAgQAAyEFAASJDkxhAAIaz2hEyV6DxFoqkj8gTkaQPuozsqklAAI0EwACWzopUL0aaltP18bBNgQ


    app.add_handler(CommandHandler("gwaifu",_gwaifu_))
    app.add_handler(CommandHandler("cwaifu",_cwaifu_))
    app.add_handler(CommandHandler("cgive",_cgive_))
    app.add_handler(CommandHandler("rgive",_rgive_))
    app.add_handler(CommandHandler("wgive",_wgive_))
    app.add_handler(CommandHandler("gpid", gpid_command))
    app.add_handler(CommandHandler("gsid", gsid_command))
    app.add_handler(CommandHandler("autoaddwaifu", autoaddwaifu))
    app.add_handler(CommandHandler("rarityadd", rarity_add))
    app.add_handler(CommandHandler("rarityedit", rarity_edit))
    app.add_handler(CommandHandler("raritylist", rarity_list))
    app.add_handler(CommandHandler("raritystickeradd", rarity_sticker_add))
    app.add_handler(CommandHandler("raritystickeredit", rarity_sticker_edit))
    app.add_handler(CommandHandler("raritystickerlist", rarity_sticker_list))
    app.add_handler(CommandHandler("setonkvid", setvid))
    # app.add_handler(CommandHandler("botstatus",Bot_status))
    app.add_handler(CommandHandler("addbypass", add_bypass))
    app.add_handler(CommandHandler("removebypass", remove_bypass))
    app.add_handler(CommandHandler("clearbypass", clear_bypass))
    
    
    app.add_handler(CommandHandler('addadmin',addadmin))
    app.add_handler(CommandHandler('removeadmin',removeadmin))
    app.add_handler(CommandHandler('listadmins',listadmins))
    app.add_handler(CommandHandler('admininfo',admininfo))
    app.add_handler(CommandHandler('isadmin',isadmin))
    app.add_handler(CommandHandler('adminstats',adminstats))

    app.add_handler(MessageHandler(filters.TEXT & filters.REPLY, guess_reply))
    app.add_handler(MessageHandler(filters.PHOTO & filters.ChatType.PRIVATE, handle_waifu_photo))

    app.add_handler(CallbackQueryHandler(handle_collection_pagination, pattern="^collection_page_"))
    app.add_handler(CallbackQueryHandler(handle_waifu_confirmation, pattern="^(confirm_waifus|cancel_waifus)$"))
    app.add_handler(CallbackQueryHandler(idol_callback, pattern=r"^idol_"))
    app.add_handler(CallbackQueryHandler(gift_confirmation, pattern="^gift_(yes|no)_"))
    # app.add_handler(CallbackQueryHandler(handle_store_callback, pattern=r"^(buy_\d+|refresh_store)$"))

    print("Bot is running!")
    app.run_polling()

if __name__ == "__main__":
    main()