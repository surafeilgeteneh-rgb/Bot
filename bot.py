import logging
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

# ========== CONFIGURATION ==========
BOT_TOKEN = "8784067730:AAEzhh9Ung97WhtZUw6NrKst65u5v7jyD2Y"
OWNER_ID = 8111368444
CHANNEL_ID = "@Qeleme_tutorial"  # Your channel username
SUPPORT_USERNAME = "@Qeleme_bot"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ========== COMMANDS ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = f"""🌟 <b>እንኳን ወደ Qeleme Tutorial በሰላም መጡ!</b> 🌟

🇪🇹 <b>በአማርኛ:</b>
📚 ኮርሱን ለመግዛት:
💳 ክፍያ: <b>ቴሌብር 0955061637</b>
👤 ስም: Seto Destawu

✅ ከክፍያ በኋላ ታች ያለውን ቁልፍ ይጫኑ

━━━━━━━━━━━━━━━━━━

🇬🇧 <b>In English:</b>
🎓 <b>Welcome to Qeleme Tutorial!</b>

💳 <b>Payment:</b> Telebirr 0955061637
👤 <b>Name:</b> Seto Destawu

✅ Tap button below after payment

━━━━━━━━━━━━━━━━━━
📞 <b>Support:</b> {SUPPORT_USERNAME}
"""
    keyboard = [
        [InlineKeyboardButton("💰 ክፍያ አስረክብ / Send Payment", callback_data="send_payment")],
        [InlineKeyboardButton("📞 ድጋፍ / Support", callback_data="support")],
        [InlineKeyboardButton("ℹ️ መመሪያ / Instructions", callback_data="instructions")]
    ]
    await update.message.reply_text(welcome, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "send_payment":
        await query.edit_message_text(
            "📸 <b>ክፍያ ማስረጃ ላኩ / Send payment screenshot</b>\n\n"
            "እባክዎ የክፍያ ማስረጃ ፎቶ ይላኩ።\n"
            "Please send your payment screenshot.",
            parse_mode='HTML'
        )
    elif query.data == "support":
        await query.edit_message_text(
            f"📞 <b>ድጋፍ / Support</b>\n\n"
            f"ማንኛውም ጥያቄ ካለዎት ያነጋግሩን:\n"
            f"For any questions, contact:\n\n"
            f"👉 {SUPPORT_USERNAME}\n\n"
            f"መልስ በ24 ሰአት ውስጥ ይሰጣል።\n"
            f"We reply within 24 hours.",
            parse_mode='HTML'
        )
    elif query.data == "instructions":
        await query.edit_message_text(
            "📖 <b>መመሪያ / Instructions</b>\n\n"
            "1️⃣ ክፍያ ይላኩ / Send payment\n"
            "2️⃣ ማስረጃ ይላኩ / Send screenshot\n"
            "3️⃣ ማጽደቅ ይጠብቁ / Wait for approval\n"
            "4️⃣ ልዩ የግብአት ሊንክ ያግኙ / Get unique invite link\n"
            "5️⃣ ቻናሉን ይቀላቀሉ / Join channel\n\n"
            "<i>ማስታወሻ:</i> ሊንክ 1 ጊዜ ብቻ ጥቅም ላይ ይውላል\n"
            "<i>Note:</i> Link is valid for 1 use only.",
            parse_mode='HTML'
        )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    photo = update.message.photo[-1]
    caption = f"🧾 አዲስ ክፍያ / New Payment\n\n👤 @{user.username}\n🆔 ID: {user.id}"
    keyboard = [[
        InlineKeyboardButton("✅ አጽድቅ / Approve", callback_data=f"approve_{user.id}"),
        InlineKeyboardButton("❌ ውድቅ አድርግ / Reject", callback_data=f"reject_{user.id}")
    ]]
    await context.bot.send_photo(chat_id=OWNER_ID, photo=photo.file_id, caption=caption, reply_markup=InlineKeyboardMarkup(keyboard))
    await update.message.reply_text("✅ ክፍያ ደርሶናል! ማጽደቅ ይጠብቁ።\nPayment received! Waiting for approval.")

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action, user_id = query.data.split('_')
    user_id = int(user_id)
    
    if action == "approve":
        link = await context.bot.create_chat_invite_link(chat_id=CHANNEL_ID, member_limit=1, expire_date=int(time.time()) + 86400)
        await context.bot.send_message(
            chat_id=user_id,
            text=f"✅ <b>ክፍያ ጸድቋል! / Payment Approved!</b>\n\n"
                 f"🔗 ልዩ የግብአት ሊንክዎ (1 ጊዜ ብቻ):\n"
                 f"Your unique invite link (1 use only):\n\n"
                 f"{link.invite_link}\n\n"
                 f"⏰ ሊንክ ከ24 ሰአት በኋላ ያበቃል\n"
                 f"Link expires in 24 hours\n\n"
                 f"📞 እገዛ ካስፈለገ: {SUPPORT_USERNAME}",
            parse_mode='HTML'
        )
        await query.edit_message_caption(caption=f"✅ Approved! Link sent to user {user_id}")
    else:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"❌ <b>ክፍያ ውድቅ ተደርጓል / Payment Rejected</b>\n\n"
                 f"እባክዎ በትክክል ይላኩ።\n"
                 f"Please resend with correct details.\n\n"
                 f"💳 ክፍያ / Payment: Telebirr 0955061637 (Seto Destawu)\n\n"
                 f"📞 እገዛ: {SUPPORT_USERNAME}",
            parse_mode='HTML'
        )
        await query.edit_message_caption(caption=f"❌ Rejected user {user_id}")

# ========== MAIN ==========
if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback, pattern="^(send_payment|support|instructions)$"))
    app.add_handler(CallbackQueryHandler(admin_callback, pattern="^(approve|reject)_"))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    # Clear any existing webhook to avoid conflicts
    print("Clearing webhook...")
    app.bot.delete_webhook(drop_pending_updates=True)
    
    # Start bot
    print("🤖 Qeleme Bot is running...")
    app.run_polling()
