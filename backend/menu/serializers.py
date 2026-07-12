"""
DRF serializers.

Read serializers expose clean, frontend-friendly JSON (absolute image URLs,
category name/slug alongside its id). Write serializers (orders) enforce
validation and snapshot prices server-side so the client cannot tamper with them.
"""

from __future__ import annotations

from decimal import Decimal

from rest_framework import serializers

from .models import Category, MenuItem, Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    """Category with a live count of its available items."""

    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "image",
            "display_order",
            "item_count",
        )

    def get_item_count(self, obj: Category) -> int:
        # Uses the annotated value from the ViewSet queryset when present.
        return getattr(obj, "available_item_count", obj.items.count())


class MenuItemSerializer(serializers.ModelSerializer):
    """A dish, with its category denormalized for convenient rendering."""

    category_name = serializers.CharField(source="category.name", read_only=True)
    category_slug = serializers.SlugField(source="category.slug", read_only=True)

    class Meta:
        model = MenuItem
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "price",
            "image",
            "is_available",
            "is_featured",
            "category",
            "category_name",
            "category_slug",
        )


class OrderItemWriteSerializer(serializers.Serializer):
    """Input for a single order line: just the item id and quantity."""

    menu_item = serializers.PrimaryKeyRelatedField(queryset=MenuItem.objects.all())
    quantity = serializers.IntegerField(min_value=1, max_value=100)

    def validate_menu_item(self, value: MenuItem) -> MenuItem:
        if not value.is_available:
            raise serializers.ValidationError(f'"{value.name}" is currently unavailable.')
        return value


class OrderItemReadSerializer(serializers.ModelSerializer):
    # Reads the stored snapshot so it survives deletion of the original dish.
    menu_item_name = serializers.CharField(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ("id", "menu_item", "menu_item_name", "quantity", "unit_price", "subtotal")


class OrderSerializer(serializers.ModelSerializer):
    """
    Read/write serializer for orders.

    On create, `items` is a list of {menu_item, quantity}. Prices are read
    from the database (never trusted from the client) and the total is
    computed server-side.
    """

    items = OrderItemWriteSerializer(many=True, write_only=True)
    order_items = OrderItemReadSerializer(source="items", many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "customer_name",
            "customer_phone",
            "address",
            "latitude",
            "longitude",
            "notes",
            "status",
            "total_amount",
            "items",
            "order_items",
            "created_at",
        )
        read_only_fields = ("status", "total_amount", "created_at")

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("An order must contain at least one item.")
        return value

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        order = Order.objects.create(**validated_data)

        total = Decimal("0.00")
        order_items = []
        for line in items_data:
            menu_item: MenuItem = line["menu_item"]
            quantity: int = line["quantity"]
            order_items.append(
                OrderItem(
                    order=order,
                    menu_item=menu_item,
                    menu_item_name=menu_item.name,  # snapshot name for history
                    quantity=quantity,
                    unit_price=menu_item.price,  # snapshot price
                )
            )
            total += menu_item.price * quantity

        OrderItem.objects.bulk_create(order_items)
        order.total_amount = total
        order.save(update_fields=["total_amount", "updated_at"])
        return order
