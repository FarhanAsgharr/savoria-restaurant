"""
URLs for the phone/WhatsApp password-reset flow.

`admin_password_reset` keeps its name so the "Forgotten your password?" link
on the admin login page points here instead of the old email flow.
"""

from django.urls import path

from . import views

urlpatterns = [
    path("admin/password_reset/", views.request_code, name="admin_password_reset"),
    path(
        "admin/password_reset/verify/",
        views.verify_code,
        name="phone_reset_verify",
    ),
]
