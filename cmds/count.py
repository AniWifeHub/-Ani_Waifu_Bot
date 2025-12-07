from telegram import Update
from telegram.ext import ContextTypes
from db.guess import guessDB
from frequently_used_functions import check_membership
from cmds.start import check_register

async def count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not await check_membership(update, context):
        return
        
    if not await check_register(update, context):
        return
    
    wCount = len(guessDB.listWaifus())

    await update.effective_message.reply_text(f"Char count = {wCount}")