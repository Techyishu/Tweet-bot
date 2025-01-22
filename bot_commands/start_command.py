from telegram import Update
from telegram.ext import ContextTypes

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Welcome new users and provide initial guidance."""
    welcome_message = (
        "👋 *Welcome to the Tweet Generator Bot!*\n\n"
        "I can help you create engaging tweets for various purposes. "
        "Here are some things you can do:\n\n"
        "• Generate tweets about any topic with /generate\n"
        "• Choose specific tweet categories with /categories\n"
        "• Set your preferences with /setpreferences\n\n"
        "Type /help to learn more about all available commands."
    )
    
    await update.message.reply_text(
        welcome_message,
        parse_mode='Markdown'
    ) 