from django.apps import AppConfig


class MenuConfig(AppConfig):
    """Configuration for the `menu` app (categories, items, orders)."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "menu"
    verbose_name = "Restaurant Menu"
