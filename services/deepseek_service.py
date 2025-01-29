import os
from typing import List
import logging
from openai import OpenAI
from utils.exceptions import OpenAIError
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

SYSTEM_PROMPT = """You are an expert social media strategist and conversational AI specializing in Tweet generation.
Transform a given headline or question into a single, engaging tweet that:
- If given a headline: Rewrite it into an engaging format with added context and insights
- If given a question: Provide a thoughtful, informative answer in tweet format
- Uses a natural, conversational tone that sounds authentically human
- Writes like a real person sharing their thoughts, not a corporate account
- Incorporates casual language, contractions, and occasional slang when appropriate
- Uses emojis naturally like a social media native would
- Includes relevant hashtags that feel organic, not forced
- Can occasionally ask rhetorical questions to engage readers
- Maintains a friendly, approachable voice

Important: Generate only ONE tweet, formatted to be easily readable and under 280 characters. The tweet should feel like it's coming from a real person having a conversation."""

async def generate_tweets(
    prompt: str,
    n: int = 1,
    update: Update = None,
    context: ContextTypes.DEFAULT_TYPE = None
) -> List[str]:
    """Generate tweets using OpenAI API."""
    try:
        logger.info(f"Attempting to generate {n} tweets")
        
        # Start typing animation if update and context are provided
        typing_message = None
        if update and context:
            typing_message = await update.message.reply_text("🤔 Generating tweets...")
            await context.bot.send_chat_action(
                chat_id=update.effective_chat.id,
                action="typing"
            )
        
        if not os.getenv("OPENAI_API_KEY"):
            logger.error("OPENAI_API_KEY not found in environment variables")
            if typing_message:
                await typing_message.delete()
            raise OpenAIError("API key not configured")

        user_prompt = f"""Create ONE engaging tweet about the headline: {prompt}

Your tweet should:
- Hook the reader in the first few words
- Include a clear value proposition or insight
- Be conversational and authentic

Important: Generate only ONE tweet, under 280 characters."""

        tweets = []
        for i in range(n):
            try:
                # Update typing message with progress for multiple tweets
                if typing_message and n > 1:
                    await typing_message.edit_text(f"🤔 Generating tweet {i+1} of {n}...")
                    await context.bot.send_chat_action(
                        chat_id=update.effective_chat.id,
                        action="typing"
                    )

                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {
                            "role": "system",
                            "content": SYSTEM_PROMPT
                        },
                        {
                            "role": "user",
                            "content": user_prompt
                        }
                    ],
                    temperature=0.8,
                    max_tokens=280,
                    presence_penalty=0.3,
                    frequency_penalty=0.3
                )
                
                tweet = response.choices[0].message.content.strip()
                # Remove any numbering or bullet points that might have been added
                tweet = tweet.lstrip('123456789.- ').strip()
                tweets.append(tweet)
                    
            except Exception as e:
                logger.error(f"Error in request: {str(e)}")
                continue
        
        # Delete the typing message
        if typing_message:
            await typing_message.delete()
        
        if not tweets:
            return ["Sorry, could not generate tweets at this time."]
            
        return tweets
            
    except Exception as e:
        # Make sure to delete typing message if there's an error
        if typing_message:
            await typing_message.delete()
        logger.error(f"Error generating tweets: {str(e)}", exc_info=True)
        raise OpenAIError(f"Error generating tweets: {str(e)}")
