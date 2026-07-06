"""
Root URL configuration.

- /admin/  → Django admin (professional CRUD dashboard)
- /api/    → REST API (wired up in Phase 1 via the `menu` app router)

During development we also serve uploaded media files (menu item images).
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def health_check(_request):
    """Lightweight liveness probe for Render / Railway health checks."""
    return JsonResponse({"status": "ok"})


urlpatterns = [
    # Phone/WhatsApp password-reset flow. Registered before the admin
    # catch-all; it defines `admin_password_reset`, so the login page's
    # "Forgotten your password?" link points to the phone flow.
    path("", include("accounts.urls")),
    path("admin/", admin.site.urls),
    path("healthz/", health_check, name="health-check"),
    # The menu app exposes the public REST API under /api/.
    path("api/", include("menu.urls")),
]

# Serve user-uploaded media during development. In production these are
# handled by the storage backend / CDN.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
