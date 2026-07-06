"""django-filter FilterSets for the API."""

import django_filters

from .models import MenuItem


class MenuItemFilter(django_filters.FilterSet):
    """
    Filter menu items by category (id or slug), availability, and price range.

    Examples:
      /api/items/?category=main-courses
      /api/items/?is_available=true&min_price=10&max_price=25
    """

    category = django_filters.CharFilter(method="filter_category")
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = MenuItem
        fields = ["category", "is_available", "is_featured"]

    def filter_category(self, queryset, name, value):
        # Accept either a numeric category id or a category slug.
        if value.isdigit():
            return queryset.filter(category_id=value)
        return queryset.filter(category__slug=value)
