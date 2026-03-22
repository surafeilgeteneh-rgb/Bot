import logging
import time
import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

# ========== CONFIGURATION ==========
BOT_TOKEN = "8784067730:AAEzhh9Ung97WhtZUw6NrKst65u5v7jyD2Y"
OWNER_ID = 8111368444
CHANNEL_ID = -1003787143260
EXPIRY_HOURS = 24
DATA_FILE = "links.json"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def load_links():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_links(links):
    with open(DATA_FILE, "w") as f:
        json.dump(links, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = (
        "🌟 <b>Welcome to Qeleme Tutorial!</b>\n\n"
        f"💰 <b>Price:</b> 200 Birr\n"
        f"💳 <b>Payment:</b> CBE\n"
        f"📞 <b>Account:</b> 1000736023184\n"
        f"👤 <b>Name:</b> MR Getachew asefa\n"
        f"⏰ <b>Your invite link will expire</b> {EXPIRY_HOURS} hours <b>after approval</b>.\n\n"
        "📞 <b>Support:</b> @Keleme_support\n\n"
        "Tap the button below after payment."
    )
    keyboard = [[InlineKeyboardButton("💰 Send Payment Proof", callback_data="send_payment")]]
    await update.message.reply_text(welcome, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "send_payment":
        await query.edit_message_text(
            "📸 <b>Send your payment screenshot</b>\n\n"
            f"Please send a screenshot of your 200 Birr payment to CBE account 1000736023184 (MR Getachew asefa).",
            parse_mode='HTML'
        )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    photo = update.message.photo[-1]
    caption = f"🧾 <b>New Payment</b>\n\n👤 @{user.username}\n🆔 ID: <code>{user.id}</code>"
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
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        await update.message.reply_text("✅ <b>Payment sent!</b>\n\nWaiting for admin approval.", parse_mode='HTML')
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
            # Create invite link with member_limit=1 and expiry
            expiry = int(time.time()) + (EXPIRY_HOURS * 3600)
            link = await context.bot.create_chat_invite_link(
                chat_id=CHANNEL_ID,
                member_limit=1,
                expire_date=expiry
            )
            # Store link info
            links = load_links()
            links[str(link.invite_link)] = {"user_id": user_id, "created": time.time()}
            save_links(links)

            # Send link to user
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    f"✅ <b>Payment Approved!</b>\n\n"
                    f"🔗 <b>Your unique invite link:</b>\n"
                    f"{link.invite_link}\n\n"
                    f"⏰ <b>Expires in:</b> {EXPIRY_HOURS} hours from now\n"
                    f"👤 <b>Valid for:</b> 1 person only\n\n"
                    f"⚠️ This link stops working after one use or after {EXPIRY_HOURS} hours.\n\n"
                    f"📞 Support: @Keleme_support"
                ),
                parse_mode='HTML'
            )
            await query.edit_message_caption(caption=f"✅ Approved! Link sent to user {user_id}")

        elif action == "incorrect":
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    f"⚠️ <b>Incorrect Payment Amount</b>\n\n"
                    f"Please pay the correct amount of <b>200 Birr</b> to CBE account 1000736023184 (MR Getachew asefa) and resend the screenshot.\n\n"
                    f"💳 <b>Payment:</b> CBE 1000736023184\n"
                    f"👤 <b>Name:</b> MR Getachew asefa\n\n"
                    f"📞 Support: @Keleme_support"
                ),
                parse_mode='HTML'
            )
            await query.edit_message_caption(caption=f"⚠️ Wrong amount sent to user {user_id}")

        elif action == "reject":
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    f"❌ <b>Payment Rejected</b>\n\n"
                    f"Please resend with correct payment details.\n\n"
                    f"💳 <b>Payment:</b> CBE 1000736023184\n"
                    f"👤 <b>Name:</b> MR Getachew asefa\n"
                    f"💰 <b>Amount:</b> 200 Birr\n\n"
                    f"📞 Support: @Keleme_support"
                ),
                parse_mode='HTML'
            )
            await query.edit_message_caption(caption=f"❌ Rejected user {user_id}")

    except Exception as e:
        logger.error(f"Admin callback error: {e}", exc_info=True)
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f"⚠️ <b>Error approving payment:</b>\n<code>{str(e)}</code>\nCheck logs.",
            parse_mode='HTML'
        )
        if 'user_id' in locals():
            await context.bot.send_message(
                chat_id=user_id,
                text="⚠️ <b>An error occurred while processing your payment.</b>\nPlease contact support @Keleme_support.",
                parse_mode='HTML'
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

        print("Clearing webhook...")
        app.bot.delete_webhook(drop_pending_updates=True)

        print("🤖 Qeleme Bot is running...")
        app.run_polling()

    except Exception as e:
        logger.critical(f"Bot failed to start: {e}")

if __name__ == "__main__":
    main()
