import logging
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

# ========== CONFIGURATION ==========
BOT_TOKEN = "8784067730:AAEzhh9Ung97WhtZUw6NrKst65u5v7jyD2Y"
OWNER_ID = 8111368444
CHANNEL_ID = -1003787143260   # Your numeric channel ID
EXPIRY_HOURS = 12

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== COMMAND HANDLERS ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = (
        "🌟 *Welcome to Qeleme Tutorial!*\n\n"
        f"💰 *Price:* 200 Birr\n"
        f"💳 *Payment:* Telebirr 0955061637\n"
        f"👤 *Name:* Seto Destawu\n"
        f"⏰ *Link expires after* {EXPIRY_HOURS} hours\n\n"
        "📞 *Support:* @Keleme_support\n\n"
        "Tap the button below after payment."
    )
    keyboard = [[InlineKeyboardButton("💰 Send Payment Proof", callback_data="send_payment")]]
    await update.message.reply_text(welcome, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "send_payment":
        await query.edit_message_text(
            "📸 *Send your payment screenshot*\n\n"
            f"Please send a screenshot of your {200} Birr payment to Telebirr 0955061637 (Seto Destawu).",
            parse_mode='Markdown'
        )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    photo = update.message.photo[-1]
    caption = f"🧾 *New Payment*\n\n👤 @{user.username}\n🆔 ID: `{user.id}`"
    keyboard = [
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user.id}"),
            InlineKeyboardButton("⚠️ Wrong Amount", callback_data=f"incorrect_{user.id}")
        ],
        [InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}")]
    ]
    try:
        await context.bot.send_photo(
            chat_id=OWNER_ID,
            photo=photo.file_id,
            caption=caption,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        await update.message.reply_text("✅ *Payment sent!*\n\nWaiting for admin approval.", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Failed to forward payment: {e}")
        await update.message.reply_text("❌ Error sending payment. Please try again or contact support.")

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        data = query.data
        action, user_id = data.split('_')
        user_id = int(user_id)

        if action == "approve":
            # Create invite link with 12h expiry and 1 user
            expiry = int(time.time()) + (EXPIRY_HOURS * 3600)
            link = await context.bot.create_chat_invite_link(
                chat_id=CHANNEL_ID,
                member_limit=1,
                expire_date=expiry
            )
            # Send link to user
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    f"✅ *Payment Approved!*\n\n"
                    f"🔗 *Your unique invite link:*\n"
                    f"{link.invite_link}\n\n"
                    f"⏰ *Expires in:* {EXPIRY_HOURS} hours\n"
                    f"👤 *Valid for:* 1 person only\n\n"
                    f"⚠️ This link stops working after one use or after {EXPIRY_HOURS} hours.\n\n"
                    f"📞 Support: @Keleme_support"
                ),
                parse_mode='Markdown'
            )
            await query.edit_message_caption(caption=f"✅ Approved! Link sent to user {user_id}")

        elif action == "incorrect":
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    f"⚠️ *Incorrect Payment Amount*\n\n"
                    f"Please pay the correct amount of *200 Birr* and resend the screenshot.\n\n"
                    f"💳 *Payment:* Telebirr 0955061637\n"
                    f"👤 *Name:* Seto Destawu\n\n"
                    f"📞 Support: @Keleme_support"
                ),
                parse_mode='Markdown'
            )
            await query.edit_message_caption(caption=f"⚠️ Wrong amount sent to user {user_id}")

        elif action == "reject":
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    f"❌ *Payment Rejected*\n\n"
                    f"Please resend with correct payment details.\n\n"
                    f"💳 *Payment:* Telebirr 0955061637\n"
                    f"👤 *Name:* Seto Destawu\n"
                    f"💰 *Amount:* 200 Birr\n\n"
                    f"📞 Support: @Keleme_support"
                ),
                parse_mode='Markdown'
            )
            await query.edit_message_caption(caption=f"❌ Rejected user {user_id}")

    except Exception as e:
        logger.error(f"Admin callback error: {e}")
        # Send error message to admin
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f"⚠️ *Error approving payment:*\n```\n{str(e)}\n```\nCheck logs.",
            parse_mode='Markdown'
        )
        # Notify user that something went wrong
        if 'user_id' in locals():
            await context.bot.send_message(
                chat_id=user_id,
                text="⚠️ *An error occurred while processing your payment.*\n"
                     "Please contact support @Keleme_support.",
                parse_mode='Markdown'
            )
        await query.edit_message_caption(caption="⚠️ Error processing. Check logs.")

# ========== MAIN ==========
def main():
    try:
        app = Application.builder().token(BOT_TOKEN).build()

        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(handle_callback, pattern="^send_payment$"))
        app.add_handler(CallbackQueryHandler(admin_callback, pattern="^(approve|incorrect|reject)_"))
        app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

        # Clear any existing webhook
        print("Clearing webhook...")
        app.bot.delete_webhook(drop_pending_updates=True)

        print("🤖 Qeleme Bot is running...")
        app.run_polling()

    except Exception as e:
        logger.critical(f"Bot failed to start: {e}")

if __name__ == "__main__":
    main()
