"""
Django Admin configuration.

Provides a professional back-office for staff: image thumbnails, inline
order items, search, filters, and read-only computed fields.
"""

from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html

from .models import Category, MenuItem, Order, OrderItem

# ── Admin branding ───────────────────────────────────────────
admin.site.site_header = "Savoria Administration"
admin.site.site_title = "Savoria Admin"
admin.site.index_title = "Restaurant management"
# "VIEW SITE" (top-right of the admin) opens the customer-facing website.
admin.site.site_url = settings.FRONTEND_URL


class MenuItemInline(admin.TabularInline):
    """Add / edit / delete a category's dishes directly on its page."""

    model = MenuItem
    extra = 1  # show one blank row so a new dish can be added immediately
    fields = ("name", "price", "is_available", "is_featured")
    show_change_link = True  # link to the item's full page (image, description)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "display_order", "item_count", "is_active", "updated_at")
    list_editable = ("display_order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("display_order", "name")
    inlines = (MenuItemInline,)

    @admin.display(description="Items")
    def item_count(self, obj: Category) -> int:
        return obj.items.count()


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = (
        "thumbnail",
        "name",
        "category",
        "price",
        "is_available",
        "is_featured",
    )
    list_display_links = ("name",)
    list_editable = ("is_available", "is_featured")
    list_filter = ("category", "is_available", "is_featured")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("category",)
    list_select_related = ("category",)
    readonly_fields = ("image_preview", "created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("name", "slug", "category", "description")}),
        ("Pricing & availability", {"fields": ("price", "is_available", "is_featured")}),
        ("Media", {"fields": ("image", "image_preview")}),
        ("Timestamps", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    @admin.display(description="Preview")
    def thumbnail(self, obj: MenuItem):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:40px;width:40px;object-fit:cover;'
                'border-radius:6px;" />',
                obj.image.url,
            )
        return "—"

    @admin.display(description="Image preview")
    def image_preview(self, obj: MenuItem):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:200px;border-radius:8px;" />',
                obj.image.url,
            )
        return "No image uploaded."


class OrderItemInline(admin.TabularInline):
    """Edit line items directly inside the Order page."""

    model = OrderItem
    extra = 0
    autocomplete_fields = ("menu_item",)
    readonly_fields = ("subtotal_display",)

    @admin.display(description="Subtotal")
    def subtotal_display(self, obj: OrderItem):
        return f"${obj.subtotal:.2f}" if obj.pk else "—"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer_name",
        "customer_phone",
        "status",
        "total_amount",
        "created_at",
    )
    # `status` editable straight from the list for quick updates.
    list_editable = ("status",)
    list_filter = ("status", "created_at")
    search_fields = ("customer_name", "customer_phone", "address")
    readonly_fields = ("total_amount", "delivery_location", "created_at", "updated_at")
    inlines = (OrderItemInline,)
    date_hierarchy = "created_at"
    fieldsets = (
        ("Customer", {"fields": ("customer_name", "customer_phone")}),
        ("Order", {"fields": ("status", "total_amount", "notes")}),
        (
            "Delivery location",
            {"fields": ("address", "latitude", "longitude", "delivery_location")},
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    @admin.display(description="Location on map")
    def delivery_location(self, obj: Order):
        """Embedded map + coordinates + Google Maps link for the delivery point."""
        if obj.latitude is None or obj.longitude is None:
            return format_html(
                "<em>No map pin (address was typed manually):</em><br>{}",
                obj.address or "—",
            )
        lat, lng = float(obj.latitude), float(obj.longitude)
        d = 0.008
        bbox = f"{lng - d},{lat - d},{lng + d},{lat + d}"
        embed = (
            f"https://www.openstreetmap.org/export/embed.html"
            f"?bbox={bbox}&layer=mapnik&marker={lat},{lng}"
        )
        gmaps = f"https://www.google.com/maps?q={lat},{lng}"
        return format_html(
            '<iframe width="100%" height="320" frameborder="0" scrolling="no" '
            'src="{}" style="border:1px solid #ccc;border-radius:8px"></iframe>'
            '<div style="margin-top:8px">📍 <strong>{}</strong><br>'
            "Coordinates: {}, {} &nbsp;·&nbsp; "
            '<a href="{}" target="_blank" rel="noopener">Open in Google Maps ↗</a></div>',
            embed,
            obj.address,
            lat,
            lng,
            gmaps,
        )

    def save_related(self, request, form, formsets, change):
        # Recompute the order total after inline items are saved.
        super().save_related(request, form, formsets, change)
        form.instance.recalculate_total()
