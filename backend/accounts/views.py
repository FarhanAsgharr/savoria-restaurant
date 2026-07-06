"""
Phone / WhatsApp password-reset views (replaces the email reset).

Flow:
  1. request_code  — enter WhatsApp number → generate + send a 6-digit code
  2. verify_code   — enter code + new password → verify → set password
"""

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import PhoneResetRequestForm, SetNewPasswordForm
from .models import PhoneResetCode, StaffProfile
from .utils import generate_code
from .whatsapp import send_whatsapp_code

User = get_user_model()

SESSION_USER = "phone_reset_user_id"
SESSION_DEV_CODE = "phone_reset_dev_code"


def request_code(request):
    """Step 1 — enter a WhatsApp number and dispatch a verification code."""
    if request.method == "POST":
        form = PhoneResetRequestForm(request.POST)
        if form.is_valid():
            phone = form.cleaned_data["phone"]
            profile = (
                StaffProfile.objects.select_related("user")
                .filter(phone=phone)
                .first()
            )
            if profile and profile.user.is_active:
                user = profile.user
                # Invalidate any outstanding codes, then issue a fresh one.
                PhoneResetCode.objects.filter(user=user, used=False).update(used=True)
                code = generate_code()
                PhoneResetCode.objects.create(user=user, code=code)

                result = send_whatsapp_code(phone, code)
                request.session[SESSION_USER] = user.pk
                # In dev/console mode, surface the code on the next screen.
                request.session[SESSION_DEV_CODE] = result.get("dev_code") or ""
                return redirect(reverse("phone_reset_verify"))

            form.add_error(
                "phone", "No active account is registered with that WhatsApp number."
            )
    else:
        form = PhoneResetRequestForm()

    return render(
        request,
        "accounts/phone_reset_request.html",
        {"form": form, "title": "Reset password"},
    )


def verify_code(request):
    """Step 2 — verify the code and set a new password."""
    user_id = request.session.get(SESSION_USER)
    if not user_id:
        return redirect(reverse("admin_password_reset"))

    dev_code = request.session.get(SESSION_DEV_CODE) or None

    if request.method == "POST":
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            entry = (
                PhoneResetCode.objects.filter(user_id=user_id, used=False)
                .order_by("-created_at")
                .first()
            )
            if not entry or not entry.is_valid():
                form.add_error(
                    "code", "This code has expired. Please request a new one."
                )
            else:
                entry.attempts += 1
                if entry.code != form.cleaned_data["code"]:
                    entry.save(update_fields=["attempts"])
                    remaining = max(0, 5 - entry.attempts)
                    form.add_error(
                        "code",
                        f"Incorrect code. {remaining} attempt(s) left.",
                    )
                else:
                    user = User.objects.get(pk=user_id)
                    user.set_password(form.cleaned_data["new_password1"])
                    user.save()
                    entry.used = True
                    entry.save(update_fields=["used", "attempts"])
                    for key in (SESSION_USER, SESSION_DEV_CODE):
                        request.session.pop(key, None)
                    messages.success(
                        request,
                        "Your password has been changed. You can now log in.",
                    )
                    return redirect(reverse("admin:login"))
    else:
        form = SetNewPasswordForm()

    return render(
        request,
        "accounts/phone_reset_verify.html",
        {"form": form, "dev_code": dev_code, "title": "Enter verification code"},
    )
