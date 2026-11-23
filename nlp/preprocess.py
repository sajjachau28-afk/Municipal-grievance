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
    """Clean English, Hindi (Devanagari), or Hinglish municipal grievance text."""
    if not isinstance(text, str) or not text.strip():
        return ""

    text = normalize_unicode(text)
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = re.sub(r"@\w+", " ", text)
    text = text.replace("#", " ")
    text = redact_pii(text)

    if lowercase:
        text = text.lower()

    text = re.sub(r"([a-zA-Z])\1{2,}", r"\1\1", text)
    text = re.sub(r"[^\u0900-\u097Fa-zA-Z0-9\[\]_\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def preprocess_dataframe(
    df: pd.DataFrame,
    text_col: str = "complaint_text",
    output_col: str = "cleaned_text",
    lowercase: bool = True,
) -> pd.DataFrame:
    """Add cleaned_text column without altering raw text or splitting data."""
    result = df.copy()
    result[output_col] = result[text_col].fillna("").astype(str).apply(
        lambda t: clean_text(t, lowercase=lowercase)
    )
    return result
