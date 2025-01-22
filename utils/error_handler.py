from telegram import Update
from telegram.ext import ContextTypes
from utils.exceptions import TweetBotError, OpenAIError, DatabaseError, ValidationError
import logging

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def handle_error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors occurring in the handlers."""
    
    # Log the error
    logger.error(f"Error: {context.error} for user {update.effective_user.id}")
    
    # Get the original error
    error = context.error
    
    try:
        raise error
    except OpenAIError:
        await update.message.reply_text(
            "😕 Sorry, there was an error generating your tweets. "
            "Please try again in a moment."
        )
    except DatabaseError:
        await update.message.reply_text(
            "😕 There was an error accessing your data. "
            "Please try again later."
        )
    except ValidationError as e:
        await update.message.reply_text(
            f"⚠️ {str(e)}\n\n"
            "Please check your input and try again."
        )
    except TweetBotError as e:
        await update.message.reply_text(
            f"❌ {str(e)}\n\n"
            "If this persists, please contact support."
        )
    except Exception as e:
        # For unexpected errors
        await update.message.reply_text(
            "😔 An unexpected error occurred. "
            "Please try again later."
        )
        # Log the full error details
        logger.exception(f"Unexpected error: {str(e)}") 