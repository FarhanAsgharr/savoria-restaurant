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


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "display_order", "item_count", "is_active", "updated_at")
    list_editable = ("display_order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("display_order", "name")

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
    list_filter = ("status", "created_at")
    search_fields = ("customer_name", "customer_phone")
    readonly_fields = ("total_amount", "created_at", "updated_at")
    inlines = (OrderItemInline,)
    date_hierarchy = "created_at"

    def save_related(self, request, form, formsets, change):
        # Recompute the order total after inline items are saved.
        super().save_related(request, form, formsets, change)
        form.instance.recalculate_total()
