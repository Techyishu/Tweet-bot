from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler
from models.subscription import SubscriptionTier, SubscriptionManager
from services.deepseek_service import generate_tweets
from models.database import Database

# Conversation states
THREAD_TOPIC = 0
THREAD_LENGTH = 1

db = Database()
subscription_manager = SubscriptionManager(db)

async def premium_features(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show available premium features."""
    user_id = update.effective_user.id
    tier = subscription_manager.get_user_subscription(user_id)
    
    if tier == SubscriptionTier.FREE:
        message = (
            "*Premium Features Available*\n\n"
            "Upgrade to Premium to unlock:\n"
            "• Twitter Thread Generation\n"
            "• Advanced Tweet Analytics\n"
            "• Priority Tweet Generation\n"
            "• Extended History Storage\n\n"
            "Use /subscribe to upgrade!"
        )
    else:
        message = (
            "*Your Premium Features*\n\n"
            "• /thread - Generate Twitter threads\n"
            "• /analytics - View tweet analytics\n"
            "• Priority tweet generation\n"
            "• Extended history storage\n\n"
            "Thank you for being a premium user!"
        )
    
    await update.message.reply_text(
        message,
        parse_mode='Markdown'
    )

async def start_thread_generation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the thread generation process."""
    user_id = update.effective_user.id
    tier = subscription_manager.get_user_subscription(user_id)
    
    if tier != SubscriptionTier.PREMIUM:
        await update.message.reply_text(
            "Thread generation is a premium feature. "
            "Use /subscribe to upgrade!"
        )
        return ConversationHandler.END
    
    await update.message.reply_text(
        "Let's create a Twitter thread!\n\n"
        "What topic would you like to create a thread about?"
    )
    return THREAD_TOPIC

async def get_thread_length(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get the desired thread length."""
    context.user_data['thread_topic'] = update.message.text
    
    keyboard = [
        [
            InlineKeyboardButton("3 tweets", callback_data="thread_3"),
            InlineKeyboardButton("5 tweets", callback_data="thread_5")
        ],
        [
            InlineKeyboardButton("7 tweets", callback_data="thread_7"),
            InlineKeyboardButton("10 tweets", callback_data="thread_10")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "How many tweets would you like in your thread?",
        reply_markup=reply_markup
    )
    return THREAD_LENGTH

async def generate_thread(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate the Twitter thread."""
    query = update.callback_query
    await query.answer()
    
    thread_length = int(query.data.split('_')[1])
    topic = context.user_data['thread_topic']
    
    prompt = (
        f"Generate a coherent Twitter thread with {thread_length} tweets about {topic}. "
        f"Make sure the tweets flow naturally and build upon each other. "
        f"Number each tweet and ensure they're connected logically."
    )
    
    tweets = await generate_tweets(prompt, n=thread_length)
    
    # Format the thread
    response = "*Your Twitter Thread*\n\n"
    for i, tweet in enumerate(tweets, 1):
        response += f"*Tweet {i}:*\n{tweet}\n\n"
    
    await query.message.edit_text(
        response,
        parse_mode='Markdown'
    )
    return ConversationHandler.END

async def cancel_thread(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel thread generation."""
    await update.message.reply_text(
        "Thread generation cancelled."
    )
    return ConversationHandler.END

async def check_subscription_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check and inform user about their subscription status."""
    user_id = update.effective_user.id
    tier = subscription_manager.get_user_subscription(user_id)
    
    if tier == SubscriptionTier.PREMIUM:
        await update.message.reply_text(
            "✅ *Active Premium Subscription*\n\n"
            "You have access to all premium features:\n"
            "• /thread - Generate Twitter threads\n"
            "• /analytics - View tweet analytics\n"
            "• Priority tweet generation\n"
            "• Extended history storage",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "❌ *No Active Premium Subscription*\n\n"
            "Upgrade to Premium to unlock:\n"
            "• Twitter Thread Generation\n"
            "• Advanced Tweet Analytics\n"
            "• Priority Tweet Generation\n"
            "• Extended History Storage\n\n"
            "Use /subscribe to upgrade!",
            parse_mode='Markdown'
        ) 