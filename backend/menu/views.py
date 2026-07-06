"""
REST API ViewSets.

- Categories & MenuItems are read-only to the public (browsing the menu).
- Orders are create-only to the public (place an order); listing/updating
  orders is reserved for staff via the Admin.

Lookups use the human-friendly `slug` so URLs match the frontend routes
(e.g. /api/categories/desserts/, /api/items/molten-chocolate-cake/).
"""

from django.db.models import Count, Q
from rest_framework import mixins, viewsets

from .filters import MenuItemFilter
from .models import Category, MenuItem, Order
from .serializers import (
    CategorySerializer,
    MenuItemSerializer,
    OrderSerializer,
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """GET list of active categories and GET a single category by slug."""

    serializer_class = CategorySerializer
    lookup_field = "slug"
    search_fields = ("name", "description")
    ordering_fields = ("display_order", "name")

    def get_queryset(self):
        # Annotate each category with a count of only its *available* items.
        return (
            Category.objects.filter(is_active=True)
            .annotate(
                available_item_count=Count(
                    "items", filter=Q(items__is_available=True)
                )
            )
            .order_by("display_order", "name")
        )


class MenuItemViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET list of menu items and GET a single item by slug.

    Supports:
      - ?category=<id|slug>     category filtering
      - ?is_available=true      availability filtering
      - ?search=<term>          search over name & description
      - ?ordering=price|-price  ordering
      - pagination (page-number)
    """

    serializer_class = MenuItemSerializer
    lookup_field = "slug"
    filterset_class = MenuItemFilter
    search_fields = ("name", "description", "category__name")
    ordering_fields = ("price", "name", "created_at")

    def get_queryset(self):
        return MenuItem.objects.select_related("category").all()


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    POST to place an order; GET /api/orders/<id>/ to retrieve one.

    Listing all orders is intentionally not exposed to the public API.
    """

    queryset = Order.objects.prefetch_related("items__menu_item").all()
    serializer_class = OrderSerializer
