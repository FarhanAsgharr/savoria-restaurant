"""Small helpers for the phone reset flow."""

import re
import secrets


def normalize_phone(raw: str) -> str:
    """Reduce a phone number to digits and an optional leading '+'.

    "+1 (555) 123-4567" → "+15551234567"
    """
    if not raw:
        return ""
    cleaned = re.sub(r"[^\d+]", "", raw)
    # Keep only a single leading '+'.
    if cleaned.startswith("+"):
        cleaned = "+" + cleaned[1:].replace("+", "")
    else:
        cleaned = cleaned.replace("+", "")
    return cleaned


def generate_code() -> str:
    """Cryptographically-random 6-digit verification code."""
    return f"{secrets.randbelow(1_000_000):06d}"
