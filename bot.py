import logging
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

# ========== CONFIGURATION ==========
BOT_TOKEN = "8754532639:AAGob1OCOjUlI2vFHGykhN6b5Pi7jUUwzo8"
OWNER_ID = 8111368444
GROUP_ID = -1003777438953  # Your group ID

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome = (
        "Welcome to Goal Tutorial!\n\n"
        "Price: 100 Birr\n\n"
        "Payment Methods:\n"
        "- Telebirr: 0955061637 (Seto Destawu)\n"
        "- CBE: 1000670894561 (Melkam Endalamaw)\n"
        "Support: @Goal_support\n\n"
        "Tap the button below after payment."
    )
    keyboard = [[InlineKeyboardButton("Send Payment Proof", callback_data="send_payment")]]
    await update.message.reply_text(welcome, reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "send_payment":
        await query.edit_message_text(
            "Send your payment screenshot.\n\n"
            "Please send a screenshot of your 100 Birr payment to:\n"
            "- Telebirr: 0955061637 (Seto Destawu)\n"
            "- CBE: 1000670894561 (Melkam Endalamaw)\n\n"
            "Make sure the screenshot shows the transaction details."
        )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ONLY process photos sent in PRIVATE CHAT - ignore group photos
    if update.effective_chat.type != "private":
        return  # Ignore photos sent in groups
    
    user = update.effective_user
    photo = update.message.photo[-1]
    caption = f"New Payment\n\n@{user.username} (ID: {user.id})"
    keyboard = [
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{user.id}"),
            InlineKeyboardButton("⚠️ Wrong Amount", callback_data=f"incorrect_{user.id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{user.id}")
        ],
        [
            InlineKeyboardButton("🤖 Bot/AI Detected", callback_data=f"bot_{user.id}"),
            InlineKeyboardButton("📸 Unclear Screenshot", callback_data=f"unclear_{user.id}")
        ],
        [
            InlineKeyboardButton("🔄 Already Paid", callback_data=f"already_{user.id}"),
            InlineKeyboardButton("💰 Refund Request", callback_data=f"refund_{user.id}")
        ],
        [
            InlineKeyboardButton("🚨 Fraudulent", callback_data=f"fraud_{user.id}"),
            InlineKeyboardButton("📱 Different Account", callback_data=f"different_{user.id}")
        ],
        [
            InlineKeyboardButton("✏️ Custom Message", callback_data=f"custom_{user.id}"),
            InlineKeyboardButton("📝 Let Student Write", callback_data=f"student_{user.id}")
        ]
    ]
    try:
        await context.bot.send_photo(
            chat_id=OWNER_ID,
            photo=photo.file_id,
            caption=caption,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        await update.message.reply_text("Payment sent! Waiting for admin approval.")
    except Exception as e:
        logger.error(f"Failed to forward payment: {e}")
        await update.message.reply_text("Error sending payment. Please try again or contact support.")

async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    try:
        data = query.data
        action, user_id = data.split('_')
        user_id = int(user_id)

        if action == "approve":
            # Create invite link for group
            link = await context.bot.create_chat_invite_link(
                chat_id=GROUP_ID,
                member_limit=1
            )
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    "✅ PAYMENT APPROVED!\n\n"
                    "Your unique invite link:\n"
                    f"{link.invite_link}\n\n"
                    "Valid for: 1 person only\n"
                    "This link stops working after one use.\n\n"
                    "Support: @Goal_support"
                )
            )
            await query.edit_message_caption(caption=f"✅ Approved! Link sent to user {user_id}")

        elif action == "incorrect":
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    "⚠️ INCORRECT PAYMENT AMOUNT\n\n"
                    "You sent the wrong amount.\n\n"
                    "Required amount: 100 Birr\n\n"
                    "Please pay the correct amount and resend your screenshot.\n\n"
                    "Payment Methods:\n"
                    "- Telebirr: 0955061637 (Seto Destawu)\n"
                    "- CBE: 1000670894561 (Melkam Endalamaw)\n\n"
                    "Support: @Goal_support"
                )
            )
            await query.edit_message_caption(caption=f"⚠️ Wrong amount sent to user {user_id}")

        elif action == "reject":
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    "❌ PAYMENT REJECTED\n\n"
                    "Your payment could not be verified.\n\n"
                    "Please resend with correct payment details.\n\n"
                    "Payment Methods:\n"
                    "- Telebirr: 0955061637 (Seto Destawu)\n"
                    "- CBE: 1000670894561 (Melkam Endalamaw)\n"
                    "Amount: 100 Birr\n\n"
                    "Support: @Goal_support"
                )
            )
            await query.edit_message_caption(caption=f"❌ Rejected user {user_id}")

        elif action == "bot":
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    "🚫 BOT / AI DETECTED - ACCESS DENIED 🚫\n\n"
                    "Our system has detected that you are using an automated bot or AI account.\n\n"
                    "⚠️ WARNING: Automated accounts are NOT permitted to join our courses.\n\n"
                    "Your payment has been flagged for review.\n\n"
                    "💰 REFUND INFORMATION:\n"
                    "- Telebirr: 0955061637 (Seto Destawu)\n"
                    "- CBE: 1000670894561 (Melkam Endalamaw)\n\n"
                    "Send your transaction details to @Goal_support for refund.\n\n"
                    "Human users only. Bots will be blocked permanently."
                )
            )
            await query.edit_message_caption(caption=f"🤖 Bot/AI detected - user {user_id}")

        elif action == "unclear":
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    "📸 UNCLEAR SCREENSHOT\n\n"
                    "Your payment screenshot is not clear or missing information.\n\n"
                    "Please send a CLEAR screenshot showing:\n"
                    "- Transaction ID\n"
                    "- Amount (100 Birr)\n"
                    "- Sender name\n"
                    "- Date and time\n\n"
                    "Resend the screenshot clearly and we will process your payment.\n\n"
                    "Support: @Goal_support"
                )
            )
            await query.edit_message_caption(caption=f"📸 Unclear screenshot - user {user_id}")

        elif action == "already":
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    "🔄 ALREADY PAID / ACTIVE MEMBER\n\n"
                    "Our records show you already have active access to our courses.\n\n"
                    "You do not need to pay again.\n\n"
                    "If you lost your invite link, contact @Goal_support for help.\n\n"
                    "If this was a duplicate payment, please contact support for refund."
                )
            )
            await query.edit_message_caption(caption=f"🔄 Already paid - user {user_id}")

        elif action == "refund":
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    "💰 REFUND REQUEST RECEIVED\n\n"
                    "To process your refund, please send the following to @Goal_support:\n\n"
                    "- Payment screenshot\n"
                    "- Transaction ID\n"
                    "- Your full name\n"
                    "- Reason for refund\n\n"
                    "Refund will be processed within 24-48 hours.\n\n"
                    "REFUND ACCOUNT:\n"
                    "- Telebirr: 0955061637 (Seto Destawu)\n"
                    "- CBE: 1000670894561 (Melkam Endalamaw)\n\n"
                    "Note: Refunds may take up to 3 business days to appear."
                )
            )
            await query.edit_message_caption(caption=f"💰 Refund request - user {user_id}")

        elif action == "fraud":
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    "🚨🚨🚨 FRAUDULENT SCREENSHOT DETECTED 🚨🚨🚨\n\n"
                    "⚠️ WARNING: Your payment screenshot appears to be FAKE or EDITED.\n\n"
                    "This is a SERIOUS VIOLATION. Fraudulent activity will result in:\n"
                    "❌ Permanent ban from all our services\n"
                    "❌ Your account reported to Telegram\n"
                    "❌ Legal action may be taken\n\n"
                    "If this was a mistake, contact @Goal_support IMMEDIATELY with PROOF.\n\n"
                    "LEGITIMATE PAYMENTS ONLY. NO EXCEPTIONS."
                )
            )
            await query.edit_message_caption(caption=f"🚨 FRAUD detected - user {user_id}")

        elif action == "different":
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    "🚨🚨🚨 MULTIPLE ACCOUNT DETECTED 🚨🚨🚨\n\n"
                    "⚠️ WARNING: This screenshot has been used with DIFFERENT Telegram accounts.\n\n"
                    "This is STRICTLY PROHIBITED.\n\n"
                    "Violation results in:\n"
                    "❌ Permanent ban for ALL associated accounts\n"
                    "❌ No refund will be issued\n"
                    "❌ Blacklisted from all future courses\n\n"
                    "Each payment is valid for ONE person only.\n\n"
                    "Contact @Goal_support if this is an error.\n\n"
                    "FRAUDULENT ACTIVITY WILL NOT BE TOLERATED."
                )
            )
            await query.edit_message_caption(caption=f"🚨 Multiple accounts - user {user_id}")

        elif action == "custom":
            # This will prompt the admin to type a custom message
            context.user_data['custom_user_id'] = user_id
            await context.bot.send_message(
                chat_id=OWNER_ID,
                text=f"✏️ Type your custom message to send to user {user_id}:\n\n(Just type the message and send)"
            )
            await query.edit_message_caption(caption=f"✏️ Custom message pending for user {user_id}")

        elif action == "student":
            await context.bot.send_message(
                chat_id=user_id,
                text=(
                    "📝 Please write your message below.\n\n"
                    "We will get back to you as soon as possible.\n\n"
                    "Support: @Goal_support"
                )
            )
            await query.edit_message_caption(caption=f"📝 Student can write - user {user_id}")

    except Exception as e:
        logger.error(f"Admin callback error: {e}", exc_info=True)
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f"Error approving payment: {str(e)}\nCheck logs."
        )
        if 'user_id' in locals():
            await context.bot.send_message(
                chat_id=user_id,
                text="An error occurred while processing your payment.\nPlease contact support @Goal_support."
            )
        await query.edit_message_caption(caption="Error processing. Check logs.")

# Handle custom message from admin
async def handle_admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    
    if 'custom_user_id' in context.user_data:
        user_id = context.user_data['custom_user_id']
        message_text = update.message.text
        
        await context.bot.send_message(
            chat_id=user_id,
            text=f"📝 Message from Admin:\n\n{message_text}\n\nSupport: @Goal_support"
        )
        
        await update.message.reply_text(f"✅ Custom message sent to user {user_id}")
        del context.user_data['custom_user_id']

def main():
    try:
        app = Application.builder().token(BOT_TOKEN).build()
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(handle_callback, pattern="^send_payment$"))
        app.add_handler(CallbackQueryHandler(admin_callback, pattern="^(approve|incorrect|reject|bot|unclear|already|refund|fraud|different|custom|student)_"))
        app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_admin_message))
        
        print("Clearing webhook...")
        app.bot.delete_webhook(drop_pending_updates=True)
        
        print("🤖 Goal Tutorial Bot is running...")
        app.run_polling()
        
    except Exception as e:
        logger.critical(f"Bot failed to start: {e}")

if __name__ == "__main__":
    main()
