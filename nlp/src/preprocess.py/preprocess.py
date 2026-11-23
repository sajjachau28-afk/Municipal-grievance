"""
Multilingual Text Preprocessing Module for Municipal Grievance Classification.
Supports English, Hindi (Devanagari script), and Hinglish (Roman / code-mixed).
"""

import re
import unicodedata
import pandas as pd


def normalize_unicode(text: str) -> str:
    """Apply NFC normalization so Hindi Devanagari matras and nukta characters stay intact."""
    return unicodedata.normalize("NFC", text)


def redact_pii(text: str) -> str:
    """Mask Indian mobile numbers and email addresses for privacy protection."""
    text = re.sub(r"\b(\+91[-\s]?)?[6-9]\d{9}\b", "[REDACTED_PHONE]", text)
    text = re.sub(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", "[REDACTED_EMAIL]", text)
    return text


def clean_text(text: str, lowercase: bool = True) -> str:
    """
    Clean a single English, Hindi, or Hinglish municipal complaint while preserving
    Devanagari characters (\u0900-\u097F), Latin letters, and meaningful numbers.
    """
    if not isinstance(text, str) or not text.strip():
        return ""

    # 1. Unicode normalization (critical for Hindi Devanagari)
    text = normalize_unicode(text)

    # 2. Remove URLs, @mentions, and '#' symbol (keep hashtag text)
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = re.sub(r"@\w+", " ", text)
    text = text.replace("#", " ")

    # 3. Redact any remaining phone numbers or emails
    text = redact_pii(text)

    # 4. Lowercase Latin characters (does not alter Devanagari characters)
    if lowercase:
        text = text.lower()

    # 5. Reduce elongated characters (e.g., 'paaaani' -> 'paani', 'plssss' -> 'plss')
    text = re.sub(r"([a-zA-Z])\1{2,}", r"\1\1", text)

    # 6. Keep only Devanagari (\u0900-\u097F), Latin letters, digits, redaction brackets, and spaces
    text = re.sub(r"[^\u0900-\u097Fa-zA-Z0-9\[\]_\s]", " ", text)

    # 7. Collapse multiple spaces/newlines into a single space
    text = re.sub(r"\s+", " ", text).strip()
    return text


def preprocess_dataframe(
    df: pd.DataFrame,
    text_col: str = "complaint_text",
    output_col: str = "cleaned_text",
    lowercase: bool = True,
) -> pd.DataFrame:
    """
    Add a cleaned text column to a DataFrame without altering the original raw text
    or performing any train-test split (to prevent data leakage).
    """
    result = df.copy()
    result[output_col] = result[text_col].fillna("").astype(str).apply(
        lambda t: clean_text(t, lowercase=lowercase)
    )
    return result