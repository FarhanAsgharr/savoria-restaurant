from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Staff accounts: phone profile + WhatsApp password-reset flow."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
    verbose_name = "Accounts & Access"

    def ready(self):
        # Wire the post_save signal that auto-creates a StaffProfile.
        from django.contrib.auth import get_user_model
        from django.db.models.signals import post_save

        from .signals import create_staff_profile

        post_save.connect(
            create_staff_profile,
            sender=get_user_model(),
            dispatch_uid="accounts.create_staff_profile",
        )
