from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.categories import TweetCategory, CATEGORY_DESCRIPTIONS

HELP_SECTIONS = {
    'basic': """
*Basic Commands*
• /generate [topic] - Generate tweets about any topic
• /categories - Choose a specific tweet category
• /setpreferences - Set your default niche and tone
• /help - Show this help message

*Examples*
• /generate AI in healthcare
• /generate productivity tips
""",
    'categories': f"""
*Available Tweet Categories*
{chr(10).join([f"• *{cat.value.title()}*: {desc}" for cat, desc in CATEGORY_DESCRIPTIONS.items()])}

Use /categories to select a category and follow the prompts.
""",
    'preferences': """
*Setting Preferences*
Use /setpreferences to set your default:
• Niche (e.g., SaaS, Marketing, Technology)
• Tone (e.g., Professional, Casual, Humorous)

Your preferences will be used automatically when generating tweets.
""",
    'tips': """
*Tips for Better Tweets*
• Be specific with your topics
• Use categories for targeted content
• Try different tones for variety
• Keep topics relevant to your niche
"""
}

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help information with interactive navigation."""
    keyboard = [
        [
            InlineKeyboardButton("Basic Commands", callback_data="help_basic"),
            InlineKeyboardButton("Categories", callback_data="help_categories")
        ],
        [
            InlineKeyboardButton("Preferences", callback_data="help_preferences"),
            InlineKeyboardButton("Tips", callback_data="help_tips")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "*Tweet Generator Bot Help*\n\n"
        "Select a topic to learn more:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def handle_help_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle help topic selection."""
    query = update.callback_query
    await query.answer()
    
    section = query.data.replace("help_", "")
    help_text = HELP_SECTIONS.get(section, "Section not found.")
    
    # Add back button
    keyboard = [[InlineKeyboardButton("« Back to Help Menu", callback_data="help_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(
        help_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def back_to_help_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Return to the main help menu."""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [
            InlineKeyboardButton("Basic Commands", callback_data="help_basic"),
            InlineKeyboardButton("Categories", callback_data="help_categories")
        ],
        [
            InlineKeyboardButton("Preferences", callback_data="help_preferences"),
            InlineKeyboardButton("Tips", callback_data="help_tips")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(
        "*Tweet Generator Bot Help*\n\n"
        "Select a topic to learn more:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    ) 