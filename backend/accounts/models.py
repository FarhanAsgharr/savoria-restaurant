"""
Staff phone profile + one-time password-reset codes.

A StaffProfile stores the WhatsApp number a reset code is sent to; a
PhoneResetCode is a short-lived, single-use verification code.
"""

from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class StaffProfile(models.Model):
    """Extra profile data for a staff/admin user (their WhatsApp number)."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="staff_profile",
    )
    phone = models.CharField(
        max_length=30,
        blank=True,
        db_index=True,
        help_text="WhatsApp number in international format, e.g. +15551234567",
    )

    def __str__(self) -> str:
        return f"{self.user.get_username()} — {self.phone or 'no phone'}"


def _default_expiry():
    return timezone.now() + timedelta(minutes=getattr(settings, "RESET_CODE_TTL_MINUTES", 10))


class PhoneResetCode(models.Model):
    """A single-use verification code sent to a user's WhatsApp number."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reset_codes",
    )
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=_default_expiry)
    used = models.BooleanField(default=False)
    attempts = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Reset code for {self.user.get_username()} ({'used' if self.used else 'active'})"

    def is_valid(self) -> bool:
        max_attempts = getattr(settings, "RESET_CODE_MAX_ATTEMPTS", 5)
        return not self.used and self.attempts < max_attempts and timezone.now() < self.expires_at
