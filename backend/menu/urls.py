"""
API URL routing for the menu app.

A DRF DefaultRouter maps ViewSets to RESTful endpoints:

  GET  /api/categories/              list active categories
  GET  /api/categories/<slug>/       category detail
  GET  /api/items/                   list menu items (filter/search/paginate)
  GET  /api/items/<slug>/            item detail
  POST /api/orders/                  place an order
  GET  /api/orders/<id>/             order detail
"""

from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, MenuItemViewSet, OrderViewSet

router = DefaultRouter()
router.register("categories", CategoryViewSet, basename="category")
router.register("items", MenuItemViewSet, basename="menuitem")
router.register("orders", OrderViewSet, basename="order")

urlpatterns = router.urls
