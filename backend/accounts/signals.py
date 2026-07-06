"""Signals for the accounts app."""

from .models import StaffProfile


def create_staff_profile(sender, instance, created, **kwargs):
    """Ensure every user has a StaffProfile (so a phone can always be set)."""
    if created:
        StaffProfile.objects.get_or_create(user=instance)
