"""
API URL routing for the menu app.

A DRF router is used so that ViewSets (added in Phase 1) automatically get
RESTful, consistently-named endpoints. The router is defined here now so the
project is runnable from Phase 0; ViewSet registrations arrive in Phase 1.
"""

from rest_framework.routers import DefaultRouter

# ViewSets will be registered on this router in Phase 1, e.g.:
#   router.register("categories", CategoryViewSet)
#   router.register("items", MenuItemViewSet)
#   router.register("orders", OrderViewSet)
router = DefaultRouter()

urlpatterns = router.urls
