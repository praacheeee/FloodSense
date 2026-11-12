
import re
import unicodedata
from typing import Dict


def normalize_text(text: str) -> str:
    """
    Normalize emergency message text without removing
    important flood-related information.
    """

    if not isinstance(text, str):
        raise TypeError("Input must be a string.")

    # Normalize Unicode characters
    text = unicodedata.normalize("NFKC", text)

    # Convert text to lowercase
    text = text.lower()

    # Remove URLs
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)

    # Remove email addresses
    text = re.sub(r"\S+@\S+\.\S+", " ", text)

    # Preserve apostrophes and meaningful punctuation
    # Replace unwanted symbols with spaces
    text = re.sub(r"[^a-z0-9\s'.,!?-]", " ", text)

    # Normalize repeated whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


def preprocess_message(text: str) -> Dict[str, str]:
    """
    Validate and preprocess one emergency message.
    Returns both original and normalized text.
    """

    if not isinstance(text, str):
        raise TypeError("Emergency message must be a string.")

    original_text = text.strip()

    if not original_text:
        raise ValueError("Emergency message cannot be empty.")

    cleaned_text = normalize_text(original_text)

    if not cleaned_text:
        raise ValueError("Message contains no usable text.")

    return {
        "original_text": original_text,
        "cleaned_text": cleaned_text
    }
