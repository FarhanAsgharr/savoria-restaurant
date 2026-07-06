"""
Root URL configuration.

- /admin/  → Django admin (professional CRUD dashboard)
- /api/    → REST API (wired up in Phase 1 via the `menu` app router)

During development we also serve uploaded media files (menu item images).
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.http import JsonResponse
from django.urls import include, path


def health_check(_request):
    """Lightweight liveness probe for Render / Railway health checks."""
    return JsonResponse({"status": "ok"})


# Password-reset flow for admin/staff accounts. Registering the
# `admin_password_reset` URL makes the "Forgotten your password?" link
# appear on the admin login page. Django's admin ships the matching
# `registration/password_reset_*.html` templates, so no extra HTML is needed.
password_reset_urls = [
    path(
        "admin/password_reset/",
        auth_views.PasswordResetView.as_view(),
        name="admin_password_reset",
    ),
    path(
        "admin/password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
]

urlpatterns = [
    # Password-reset routes must be registered before the admin catch-all.
    *password_reset_urls,
    path("admin/", admin.site.urls),
    path("healthz/", health_check, name="health-check"),
    # The menu app exposes the public REST API under /api/.
    path("api/", include("menu.urls")),
]

# Serve user-uploaded media during development. In production these are
# handled by the storage backend / CDN.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
