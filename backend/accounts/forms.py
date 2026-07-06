"""Forms for the phone-based password reset."""

from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .utils import normalize_phone


class PhoneResetRequestForm(forms.Form):
    """Step 1: the user enters their registered WhatsApp number."""

    phone = forms.CharField(
        label="WhatsApp number",
        max_length=30,
        widget=forms.TextInput(attrs={"placeholder": "+1 555 123 4567", "autocomplete": "tel"}),
    )

    def clean_phone(self) -> str:
        return normalize_phone(self.cleaned_data["phone"])


class SetNewPasswordForm(forms.Form):
    """Step 2: the user enters the code and their new password."""

    code = forms.CharField(
        label="Verification code",
        max_length=6,
        widget=forms.TextInput(attrs={"inputmode": "numeric", "autocomplete": "one-time-code"}),
    )
    new_password1 = forms.CharField(
        label="New password", widget=forms.PasswordInput(attrs={"autocomplete": "new-password"})
    )
    new_password2 = forms.CharField(
        label="Confirm new password",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    def clean_code(self) -> str:
        return self.cleaned_data["code"].strip()

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("new_password1")
        p2 = cleaned.get("new_password2")
        if p1 and p2 and p1 != p2:
            self.add_error("new_password2", "The two password fields didn't match.")
        if p1:
            try:
                validate_password(p1)
            except ValidationError as exc:
                self.add_error("new_password1", exc)
        return cleaned
