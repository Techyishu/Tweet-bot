from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, filters
from models.database import Database

# Conversation states
CHOOSING_NICHE = 0
CHOOSING_TONE = 1

# Available options
NICHES = ['SaaS', 'Marketing', 'Technology', 'Business', 'Other']
TONES = ['Professional', 'Casual', 'Humorous', 'Educational']

db = Database()

async def start_preferences(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the preferences setting conversation."""
    keyboard = [[niche] for niche in NICHES]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    
    await update.message.reply_text(
        "Let's set your tweet preferences!\n\n"
        "First, choose your preferred niche:",
        reply_markup=reply_markup
    )
    return CHOOSING_NICHE

async def save_niche(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save the chosen niche and ask for tone."""
    context.user_data['niche'] = update.message.text
    
    keyboard = [[tone] for tone in TONES]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    
    await update.message.reply_text(
        "Great! Now choose your preferred tone:",
        reply_markup=reply_markup
    )
    return CHOOSING_TONE

async def save_tone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save the chosen tone and complete the preferences setting."""
    user_id = update.effective_user.id
    preferences = {
        'niche': context.user_data['niche'],
        'tone': update.message.text
    }
    
    db.set_user_preferences(user_id, preferences)
    
    await update.message.reply_text(
        f"Perfect! Your preferences have been saved:\n"
        f"Niche: {preferences['niche']}\n"
        f"Tone: {preferences['tone']}\n\n"
        f"These will be used as defaults when generating tweets.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the preferences setting conversation."""
    await update.message.reply_text(
        "Preferences setting cancelled.",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END 