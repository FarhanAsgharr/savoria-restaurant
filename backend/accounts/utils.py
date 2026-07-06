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


def find_profile_by_phone(raw: str):
    """Find a StaffProfile whose phone matches, tolerant of formatting.

    Matches on full digit string OR the last 10 digits, so a number entered
    with/without the country code, spaces, dashes or a leading '+' still
    resolves to the same account.
    """
    from .models import StaffProfile  # local import avoids circular import

    digits = re.sub(r"\D", "", raw or "")
    if not digits:
        return None
    tail = digits[-10:]
    for profile in StaffProfile.objects.exclude(phone="").select_related("user"):
        stored = re.sub(r"\D", "", profile.phone)
        if stored and (stored == digits or stored[-10:] == tail):
            return profile
    return None
