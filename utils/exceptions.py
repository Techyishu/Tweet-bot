class TweetBotError(Exception):
    """Base exception class for Tweet Generator Bot."""
    pass

class OpenAIError(TweetBotError):
    """Raised when there's an error with OpenAI API."""
    pass

class DatabaseError(TweetBotError):
    """Raised when there's a database error."""
    pass

class ValidationError(TweetBotError):
    """Raised when input validation fails."""
    pass

class SubscriptionError(TweetBotError):
    """Raised when there's an error with subscription handling."""
    pass 