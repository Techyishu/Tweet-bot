from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters, CallbackQueryHandler, PreCheckoutQueryHandler
import os
from dotenv import load_dotenv
from services.deepseek_service import generate_tweets
from bot_commands.preferences import (
    start_preferences, save_niche, save_tone, cancel,
    CHOOSING_NICHE, CHOOSING_TONE, NICHES, TONES
)
from models.database import Database
from bot_commands.category_commands import (
    categories, 
    handle_category_selection, 
    handle_topic
)
from bot_commands.help_command import (
    help_command,
    handle_help_selection,
    back_to_help_menu
)
from bot_commands.start_command import start_command
from bot_commands.history_commands import (
    history_command,
    view_history_entry,
    back_to_history
)
from bot_commands.premium_commands import (
    premium_features,
    start_thread_generation,
    get_thread_length,
    generate_thread,
    cancel_thread,
    THREAD_TOPIC,
    THREAD_LENGTH,
    check_subscription_status
)
from services.payment_service import (
    send_payment_options,
    handle_subscription_selection,
    handle_successful_payment,
    precheckout_callback
)
from utils.error_handler import handle_error
from utils.validation import validate_topic
import logging
import logging.handlers

load_dotenv()

db = Database()

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate tweets with error handling."""
    try:
        user_id = update.effective_user.id
        user_input = " ".join(context.args)
        
        # Validate input
        topic = validate_topic(user_input)
        
        # Update user's last active timestamp
        db.update_last_active(user_id)
        
        # Get user preferences
        preferences = db.get_user_preferences(user_id)
        if preferences:
            niche = preferences.get('niche', 'General')
            tone = preferences.get('tone', 'Professional')
        else:
            niche = 'General'
            tone = 'Professional'
        
        prompt = (
            f"Generate 3 tweets about {topic} "
            f"for the {niche} niche in a {tone} tone."
        )
        
        # Pass update and context to generate_tweets
        tweets = await generate_tweets(prompt, update=update, context=context)
        
        # Store in history
        input_data = {
            'topic': topic,
            'niche': niche,
            'tone': tone
        }
        db.add_tweet_history(user_id, input_data, tweets)
        
        response = "\n\n".join(tweets)
        await update.message.reply_text(f"Here are your tweets:\n\n{response}")
        
    except Exception as e:
        # Let the error handler deal with it
        raise

# Set up logging
def setup_logging():
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure logging with a higher level for httpx
    logging.getLogger('httpx').setLevel(logging.WARNING)  # Only show warnings and errors
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    
    # Configure main logging
    logging.basicConfig(
        level=logging.INFO,  # Changed from DEBUG to INFO
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.handlers.RotatingFileHandler(
                'logs/bot.log',
                maxBytes=1024*1024,
                backupCount=5
            ),
            logging.StreamHandler()  # For console output
        ]
    )

if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting bot application")
    
    app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    
    # Add error handler
    app.add_error_handler(handle_error)
    
    # Add the generate command handler
    app.add_handler(CommandHandler("generate", generate))
    
    # Add the preferences conversation handler
    preferences_handler = ConversationHandler(
        entry_points=[CommandHandler('setpreferences', start_preferences)],
        states={
            CHOOSING_NICHE: [MessageHandler(filters.Text(NICHES), save_niche)],
            CHOOSING_TONE: [MessageHandler(filters.Text(TONES), save_tone)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    app.add_handler(preferences_handler)
    
    # Add category-related handlers
    app.add_handler(CommandHandler("categories", categories))
    app.add_handler(CallbackQueryHandler(handle_category_selection, pattern="^category_"))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.UpdateType.MESSAGE,
        handle_topic
    ))
    
    # Add help command handlers
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(
        handle_help_selection,
        pattern="^help_(?!main)[a-zA-Z]+$"
    ))
    app.add_handler(CallbackQueryHandler(
        back_to_help_menu,
        pattern="^help_main$"
    ))
    
    # Add start command handler
    app.add_handler(CommandHandler("start", start_command))
    
    # Add history-related handlers
    app.add_handler(CommandHandler("history", history_command))
    app.add_handler(CallbackQueryHandler(
        view_history_entry,
        pattern="^history_view_[0-9]+$"
    ))
    app.add_handler(CallbackQueryHandler(
        back_to_history,
        pattern="^history_back$"
    ))
    
    # Add premium feature handlers
    app.add_handler(CommandHandler("premium", premium_features))
    
    # Add thread generation conversation handler
    thread_handler = ConversationHandler(
        entry_points=[CommandHandler('thread', start_thread_generation)],
        states={
            THREAD_TOPIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_thread_length)],
            THREAD_LENGTH: [CallbackQueryHandler(generate_thread, pattern='^thread_[0-9]+$')]
        },
        fallbacks=[CommandHandler('cancel', cancel_thread)]
    )
    app.add_handler(thread_handler)
    
    # Add subscription/payment handlers
    app.add_handler(CommandHandler("subscribe", send_payment_options))
    app.add_handler(CallbackQueryHandler(
        handle_subscription_selection,
        pattern="^subscribe_(monthly|yearly)$"
    ))
    app.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    app.add_handler(MessageHandler(
        filters.SUCCESSFUL_PAYMENT,
        handle_successful_payment
    ))
    
    # Add subscription status handler
    app.add_handler(CommandHandler("status", check_subscription_status))
    
    app.run_polling() 