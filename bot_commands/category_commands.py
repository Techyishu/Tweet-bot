from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler, CommandHandler
from utils.categories import TweetCategory, CATEGORY_DESCRIPTIONS, get_category_prompt
from services.deepseek_service import generate_tweets
from models.database import Database
from utils.exceptions import ValidationError
from utils.validation import validate_topic

db = Database()

async def categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show available tweet categories."""
    keyboard = []
    for category in TweetCategory:
        keyboard.append([
            InlineKeyboardButton(
                category.value.title(), 
                callback_data=f"category_{category.value}"
            )
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Choose a category for your tweet:\n\n" +
        "\n".join([
            f"• *{cat.value.title()}*: {desc}"
            for cat, desc in CATEGORY_DESCRIPTIONS.items()
        ]),
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_category_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle category selection and generate tweets."""
    query = update.callback_query
    await query.answer()
    
    # Extract category from callback data
    category_name = query.data.replace("category_", "")
    category = TweetCategory(category_name)
    
    # Get user preferences
    user_id = update.effective_user.id
    preferences = db.get_user_preferences(user_id)
    if preferences:
        niche = preferences.get('niche', 'General')
        tone = preferences.get('tone', 'Professional')
    else:
        niche = 'General'
        tone = 'Professional'
    
    # Store category in context for the next step
    context.user_data['selected_category'] = category
    
    # Ask for topic
    await query.message.reply_text(
        f"You've selected the {category.value.title()} category.\n"
        f"Please enter your topic:"
    )
    # Set up for the next message to be handled by generate_category_tweet
    context.user_data['awaiting_topic'] = True

async def handle_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the topic input for a category."""
    topic = update.message.text
    category = context.user_data.get('selected_category')
    
    if not category:
        await update.message.reply_text(
            "Please select a category first using /categories"
        )
        return
    
    try:
        topic = validate_topic(topic)
        prompt = get_category_prompt(category, topic)
        
        # Pass update and context to generate_tweets
        tweets = await generate_tweets(prompt, update=update, context=context)
        
        response = "\n\n".join(f"{i+1}. {tweet}" for i, tweet in enumerate(tweets))
        await update.message.reply_text(
            f"Here are your {category.value} tweets about {topic}:\n\n{response}"
        )
        
    except ValidationError as e:
        await update.message.reply_text(str(e))
    finally:
        # Clear the awaiting_topic flag
        context.user_data['awaiting_topic'] = False 