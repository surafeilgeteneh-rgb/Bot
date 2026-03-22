import logging
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

# ========== CONFIGURATION ==========
BOT_TOKEN = "8784067730:AAEzhh9Ung97WhtZUw6NrKst65u5v7jyD2Y"
OWNER_ID = 8111368444
CHANNEL_ID = "@Qeleme_tutorial"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ========== COMMANDS ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = """🌟 Welcome to Qeleme Tutorial!

💰 Price: 200 Birr
💳 Payment: Telebirr 0955061637
👤 Name: Seto Destawu

📞 Support: @Keleme_support

Tap button below after payment."""
    keyboard = [[InlineKeyboardButton("💰 Send Payment Proof", callback_data="send_payment")]]
    await update.message.reply_text(welcome, reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "send_payment":
        await query.edit_message_text("📸 Send your payment screenshot (200 Birr).")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    photo = update.message.photo[-1]
    caption = f"Payment from @{user.username} (ID: {user.id})"
    keyboard = [
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user.id}"),
            InlineKeyboardButton("⚠️ Pay Correct Amount", callback_data=f"incorrect_{user.id}")
        ],
        [InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}")]
    ]
    await context.bot.send_photo(chat_id=OWNER_ID, photo=photo.file_id, caption=caption, reply_markup=InlineKeyboardMarkup(keyboard))
    await update.message.reply_text("✅ Payment sent! Waiting for approval.")

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action, user_id = query.data.split('_')
    user_id = int(user_id)
    
    if action == "approve":
        link = await context.bot.create_chat_invite_link(chat_id=CHANNEL_ID, member_limit=1, expire_date=int(time.time()) + 86400)
        await context.bot.send_message(chat_id=user_id, text=f"✅ Approved! Your link: {link.invite_link}")
        await query.edit_message_caption(caption=f"✅ Approved! Link sent")
    
    elif action == "incorrect":
        await context.bot.send_message(chat_id=user_id, text="⚠️ Please pay the correct amount (200 Birr) and resend screenshot.\n\n💳 Telebirr: 0955061637\n👤 Seto Destawu\n📞 Support: @Keleme_support")
        await query.edit_message_caption(caption=f"⚠️ Incorrect amount")
    
    elif action == "reject":
        await context.bot.send_message(chat_id=user_id, text="❌ Payment rejected. Please resend with correct details.\n📞 Support: @Keleme_support")
        await query.edit_message_caption(caption=f"❌ Rejected")

# ========== MAIN ==========
if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback, pattern="send_payment"))
    app.add_handler(CallbackQueryHandler(admin_callback, pattern="^(approve|incorrect|reject)_"))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("Clearing webhook...")
    app.bot.delete_webhook(drop_pending_updates=True)
    
    print("🤖 Qeleme Bot is running...")
    app.run_polling()
