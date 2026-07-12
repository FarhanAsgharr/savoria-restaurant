from django.db import migrations


def backfill_names(apps, schema_editor):
    """Copy the current menu item name into each existing order line."""
    OrderItem = apps.get_model("menu", "OrderItem")
    for item in OrderItem.objects.select_related("menu_item").all():
        if not item.menu_item_name and item.menu_item_id:
            item.menu_item_name = item.menu_item.name
            item.save(update_fields=["menu_item_name"])


class Migration(migrations.Migration):

    dependencies = [
        ("menu", "0004_orderitem_menu_item_name_alter_orderitem_menu_item"),
    ]

    operations = [
        migrations.RunPython(backfill_names, migrations.RunPython.noop),
    ]
