from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from models.database import Database
from datetime import datetime
import json

db = Database()

async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show user's tweet generation history."""
    user_id = update.effective_user.id
    history = db.get_user_history(user_id)
    
    if not history:
        await update.message.reply_text(
            "You haven't generated any tweets yet. Use /generate to create some!"
        )
        return
    
    # Create a formatted message with the history
    message = "*Your Recent Tweet History*\n\n"
    for i, entry in enumerate(history, 1):
        input_data = entry['input_data']
        tweets = entry['generated_tweets']
        created_at = datetime.strptime(entry['created_at'], '%Y-%m-%d %H:%M:%S')
        
        message += f"*{i}. Generated on {created_at.strftime('%Y-%m-%d %H:%M')}*\n"
        message += f"Topic: {input_data.get('topic', 'N/A')}\n"
        if 'category' in input_data:
            message += f"Category: {input_data['category']}\n"
        message += f"First tweet: {tweets[0][:100]}...\n\n"
    
    # Add buttons to view full details of each entry
    keyboard = []
    for i in range(len(history)):
        keyboard.append([InlineKeyboardButton(
            f"View Full Entry #{i+1}",
            callback_data=f"history_view_{i}"
        )])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def view_history_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show full details of a specific history entry."""
    query = update.callback_query
    await query.answer()
    
    # Extract entry index from callback data
    entry_index = int(query.data.split('_')[-1])
    user_id = update.effective_user.id
    history = db.get_user_history(user_id)
    
    if not history or entry_index >= len(history):
        await query.message.edit_text("Entry not found.")
        return
    
    entry = history[entry_index]
    input_data = entry['input_data']
    tweets = entry['generated_tweets']
    created_at = datetime.strptime(entry['created_at'], '%Y-%m-%d %H:%M:%S')
    
    # Format the full entry details
    message = (
        f"*Tweet Generation Details*\n"
        f"Generated on: {created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
        f"*Input Parameters:*\n"
        f"• Topic: {input_data.get('topic', 'N/A')}\n"
        f"• Category: {input_data.get('category', 'N/A')}\n"
        f"• Niche: {input_data.get('niche', 'N/A')}\n"
        f"• Tone: {input_data.get('tone', 'N/A')}\n\n"
        f"*Generated Tweets:*\n"
    )
    
    for i, tweet in enumerate(tweets, 1):
        message += f"\n{i}. {tweet}\n"
    
    # Add back button
    keyboard = [[InlineKeyboardButton("« Back to History", callback_data="history_back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.message.edit_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def back_to_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Return to the main history view."""
    query = update.callback_query
    await query.answer()
    
    # Recreate the history view
    await history_command(update, context) 