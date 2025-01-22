from typing import Dict, List
from enum import Enum

class TweetCategory(Enum):
    EDUCATIONAL = "educational"
    STORYTELLING = "storytelling"
    INSPIRATIONAL = "inspirational"

CATEGORY_DESCRIPTIONS = {
    TweetCategory.EDUCATIONAL: "Informational tweets that teach or explain concepts",
    TweetCategory.STORYTELLING: "Narrative tweets that share experiences or anecdotes",
    TweetCategory.INSPIRATIONAL: "Motivational tweets that inspire and encourage"
}

CATEGORY_PROMPTS = {
    TweetCategory.EDUCATIONAL: (
        "Write a concise and educational tweet about '{topic}' that teaches the reader "
        "something valuable. Focus on the {niche} niche with a {tone} tone. "
        "Include a key insight or statistic if relevant."
    ),
    TweetCategory.STORYTELLING: (
        "Create a compelling story-based tweet about '{topic}' that resonates with "
        "readers in the {niche} space. Use a {tone} tone and focus on a specific "
        "moment or experience that delivers value."
    ),
    TweetCategory.INSPIRATIONAL: (
        "Compose an inspiring tweet about '{topic}' that motivates readers in the "
        "{niche} field. Maintain a {tone} tone while encouraging action or "
        "perspective shift."
    )
}

def get_category_prompt(category: TweetCategory, topic: str, niche: str, tone: str) -> str:
    """Generate a specific prompt based on the category and parameters."""
    base_prompt = CATEGORY_PROMPTS[category]
    return base_prompt.format(topic=topic, niche=niche, tone=tone) 