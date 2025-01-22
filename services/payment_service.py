from telegram import LabeledPrice, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, PreCheckoutQueryHandler
import os
from models.subscription import SubscriptionManager, SubscriptionTier
from models.database import Database

PREMIUM_MONTHLY_PRICE = 999  # $9.99 in cents
PREMIUM_YEARLY_PRICE = 9999  # $99.99 in cents

db = Database()
subscription_manager = SubscriptionManager(db)

async def send_payment_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send subscription payment options to user."""
    keyboard = [
        [
            InlineKeyboardButton(
                "Monthly - $9.99",
                callback_data="subscribe_monthly"
            )
        ],
        [
            InlineKeyboardButton(
                "Yearly - $99.99 (Save 16%)",
                callback_data="subscribe_yearly"
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "*Premium Subscription*\n\n"
        "Choose your subscription plan:\n\n"
        "Benefits include:\n"
        "• Twitter Thread Generation\n"
        "• Advanced Tweet Analytics\n"
        "• Priority Tweet Generation\n"
        "• Extended History Storage",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_subscription_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle subscription plan selection."""
    query = update.callback_query
    await query.answer()
    
    plan = query.data.split('_')[1]
    
    if plan == "monthly":
        await send_invoice(
            update,
            context,
            "Monthly Premium",
            "Monthly subscription to Tweet Generator Premium",
            PREMIUM_MONTHLY_PRICE,
            30
        )
    else:
        await send_invoice(
            update,
            context,
            "Yearly Premium",
            "Yearly subscription to Tweet Generator Premium",
            PREMIUM_YEARLY_PRICE,
            365
        )

async def send_invoice(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    title: str,
    description: str,
    price: int,
    duration: int
):
    """Send payment invoice to user."""
    chat_id = update.effective_chat.id
    
    # Store duration in context for use after payment
    context.user_data['subscription_duration'] = duration
    
    await context.bot.send_invoice(
        chat_id=chat_id,
        title=title,
        description=description,
        payload=f"premium_{duration}",
        provider_token=os.getenv('PAYMENT_PROVIDER_TOKEN'),
        currency="USD",
        prices=[LabeledPrice("Premium Subscription", price)],
        need_name=True,
        need_email=True
    )

async def handle_successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process successful payment and activate subscription."""
    user_id = update.effective_user.id
    duration = int(update.message.successful_payment.invoice_payload.split('_')[1])
    
    # Activate premium subscription
    subscription_manager.set_premium_subscription(user_id, duration)
    
    await update.message.reply_text(
        "🎉 *Welcome to Premium!*\n\n"
        "Your premium subscription has been activated. "
        "You now have access to all premium features:\n\n"
        "• Use /thread to create Twitter threads\n"
        "• Use /analytics for tweet analysis\n"
        "• Priority tweet generation\n"
        "• Extended history storage\n\n"
        "Thank you for your support!",
        parse_mode='Markdown'
    )

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the pre-checkout callback."""
    query = update.pre_checkout_query
    await query.answer(ok=True) 