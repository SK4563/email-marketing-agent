import re
from datetime import datetime
from typing import Any, Dict, List, Optional


def validate_email(email: str) -> bool:
    """
    Validates an email address string using a broad regex pattern.

    Args:
        email: The email address string to validate.

    Returns:
        True if the email format is valid, False otherwise.
    """
    if not email:
        return False
    # General regular expression for email validation
    pattern = r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$"
    return re.match(pattern, email) is not None


def format_currency(amount: float, currency_code: str = 'USD') -> str:
    """
    Formats a numeric amount into a currency string.

    Args:
        amount: The numeric value to format.
        currency_code: The ISO currency code (default 'USD').

    Returns:
        A formatted currency string.
    """
    return f"{currency_code} ${amount:,.2f}"


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncates a block of text to a specified maximum length, appending ellipses.

    Args:
        text: The text to truncate.
        max_length: The maximum allowed length.

    Returns:
        The truncated text.
    """
    if len(text) <= max_length:
        return text
    return text[:max_length].rstrip() + "..."


def get_timestamp() -> str:
    """
    Returns the current universal timestamp formatted as a string.

    Returns:
        Current UTC timestamp in YYYY-MM-DD HH:MM:SS format.
    """
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def clean_dict_keys(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively cleans keys in a dictionary (strips whitespace, lowers case).

    Args:
        data: The input dictionary.

    Returns:
        A new dictionary with cleaned keys.
    """
    cleaned = {}
    for key, value in data.items():
        new_key = key.strip().lower().replace(" ", "_")
        if isinstance(value, dict):
            cleaned[new_key] = clean_dict_keys(value)
        elif isinstance(value, list):
            cleaned[new_key] = [clean_dict_keys(item) if isinstance(item, dict) else item for item in value]
        else:
            cleaned[new_key] = value
    return cleaned


def extract_keywords(text: str, num_keywords: int = 5) -> List[str]:
    """
    Extracts basic keywords from text by filtering out short words and standardizing.

    Args:
        text: Input text corpus.
        num_keywords: Maximum number of keywords to return.

    Returns:
        A list of distinct keywords.
    """
    # Simple tokenization and normalization
    words = re.findall(r'\b\w{4,}\b', text.lower())
    
    # Primitive stop words list relevant to context
    stop_words = {'this', 'that', 'with', 'from', 'estimation', 'project', 'service', 'takeoff'}
    
    filtered_words = [word for word in words if word not in stop_words]
    
    # Get unique words preserving rudimentary frequency order implicitly
    seen = set()
    distinct_keywords = []
    for word in filtered_words:
        if word not in seen:
            distinct_keywords.append(word)
            seen.add(word)
            if len(distinct_keywords) == num_keywords:
                break
                
    return distinct_keywords
