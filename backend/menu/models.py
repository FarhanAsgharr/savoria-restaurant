"""
Data models for the restaurant menu & ordering system.

  Category   1 ─── * MenuItem
  Order      1 ─── * OrderItem  * ─── 1 MenuItem

All models carry created/updated timestamps and are validated at the
model layer so that both the Admin and the API enforce the same rules.
"""

from __future__ import annotations

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class TimeStampedModel(models.Model):
    """Abstract base adding self-managing created/updated timestamps (DRY)."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStampedModel):
    """A menu section, e.g. 'Starters', 'Main Courses', 'Desserts'."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True,
        help_text="URL-friendly identifier. Auto-generated from the name if left blank.",
    )
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    is_active = models.BooleanField(
        default=True, help_text="Inactive categories are hidden from the public API."
    )
    display_order = models.PositiveIntegerField(default=0, help_text="Lower numbers appear first.")

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["display_order", "name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        # Auto-slug on first save (kept stable afterwards to avoid breaking URLs).
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class MenuItem(TimeStampedModel):
    """A single dish belonging to a category."""

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="items",
    )
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )
    image = models.ImageField(upload_to="menu_items/", blank=True, null=True)
    is_available = models.BooleanField(
        default=True, help_text="Unavailable items are shown but cannot be ordered."
    )
    is_featured = models.BooleanField(
        default=False, help_text="Featured dishes are highlighted on the home page."
    )

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_available"]),
        ]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            base = slugify(self.name)
            slug = base
            # Guarantee uniqueness even for duplicate dish names.
            counter = 1
            while MenuItem.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                counter += 1
                slug = f"{base}-{counter}"
            self.slug = slug
        super().save(*args, **kwargs)


class Order(TimeStampedModel):
    """A customer order composed of one or more OrderItems."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        PREPARING = "preparing", "Preparing"
        READY = "ready", "Ready"
        OUT_FOR_DELIVERY = "out_for_delivery", "Out for Delivery"
        DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"

    customer_name = models.CharField(max_length=150)
    customer_phone = models.CharField(max_length=30)
    address = models.TextField(help_text="Delivery address (selected on the map).")
    # Coordinates of the delivery address, picked on the map at checkout.
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    notes = models.TextField(blank=True, help_text="Special requests.")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    # Set automatically the moment the order is marked Delivered.
    delivered_at = models.DateTimeField(null=True, blank=True, editable=False)
    # Snapshot of the order total at creation time (immune to later price changes).
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Order #{self.pk} — {self.customer_name}"

    def save(self, *args, **kwargs) -> None:
        # Stamp the delivery time when marked Delivered; clear it otherwise.
        if self.status == self.Status.DELIVERED and self.delivered_at is None:
            self.delivered_at = timezone.now()
        elif self.status != self.Status.DELIVERED:
            self.delivered_at = None
        update_fields = kwargs.get("update_fields")
        if update_fields is not None:
            kwargs["update_fields"] = set(update_fields) | {"delivered_at"}
        super().save(*args, **kwargs)

    def recalculate_total(self, *, commit: bool = True) -> Decimal:
        """Recompute total_amount from the related order items."""
        total = sum((item.subtotal for item in self.items.all()), start=Decimal("0.00"))
        self.total_amount = total
        if commit:
            self.save(update_fields=["total_amount", "updated_at"])
        return total


class ActiveOrder(Order):
    """Proxy: orders that are not yet delivered (the working queue)."""

    class Meta:
        proxy = True
        verbose_name = "Active Order"
        verbose_name_plural = "Active Orders"


class DeliveredOrder(Order):
    """Proxy: completed (delivered) orders."""

    class Meta:
        proxy = True
        verbose_name = "Delivered Order"
        verbose_name_plural = "Delivered Orders"


class OrderItem(models.Model):
    """A line item: a quantity of one MenuItem within an Order."""

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    # SET_NULL (not PROTECT) so a dish/category can be deleted without blocking;
    # the order line keeps its own name + price snapshot for history.
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_items",
    )
    # Name + price captured at order time so history survives item deletion.
    menu_item_name = models.CharField(max_length=150, blank=True)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        ordering = ["id"]

    def __str__(self) -> str:
        name = self.menu_item_name or (self.menu_item.name if self.menu_item else "deleted item")
        return f"{self.quantity} × {name}"

    @property
    def subtotal(self) -> Decimal:
        return self.unit_price * self.quantity
