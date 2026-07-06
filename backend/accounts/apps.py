from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Staff accounts: phone profile + WhatsApp password-reset flow."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "accounts"
    verbose_name = "Accounts & Access"
