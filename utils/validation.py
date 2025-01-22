from utils.exceptions import ValidationError

def validate_topic(topic: str) -> str:
    """Validate and clean topic input."""
    if not topic:
        raise ValidationError("Topic cannot be empty.")
    
    topic = topic.strip()
    if len(topic) < 3:
        raise ValidationError("Topic must be at least 3 characters long.")
    
    if len(topic) > 100:
        raise ValidationError("Topic must be less than 100 characters.")
    
    return topic

def validate_user_input(text: str, min_length: int = 3, max_length: int = 100) -> str:
    """Generic input validation."""
    if not text:
        raise ValidationError("Input cannot be empty.")
    
    text = text.strip()
    if len(text) < min_length:
        raise ValidationError(f"Input must be at least {min_length} characters long.")
    
    if len(text) > max_length:
        raise ValidationError(f"Input must be less than {max_length} characters.")
    
    return text 