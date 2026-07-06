"""Tests for the accounts app: profile signal, phone matching, reset flow."""

from datetime import timedelta

from django.contrib.auth import authenticate, get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from accounts.models import PhoneResetCode, StaffProfile
from accounts.utils import find_profile_by_phone, generate_code, normalize_phone

User = get_user_model()


class ProfileSignalTests(TestCase):
    def test_profile_created_with_user(self):
        user = User.objects.create_user("chef", password="x")
        self.assertTrue(StaffProfile.objects.filter(user=user).exists())


class PhoneUtilTests(TestCase):
    def test_normalize_phone(self):
        self.assertEqual(normalize_phone("+1 (555) 123-4567"), "+15551234567")
        self.assertEqual(normalize_phone("0331 398 8471"), "03313988471")

    def test_generate_code_is_six_digits(self):
        code = generate_code()
        self.assertEqual(len(code), 6)
        self.assertTrue(code.isdigit())

    def test_find_profile_tolerant_of_format(self):
        user = User.objects.create_user("mgr", password="x")
        user.staff_profile.phone = "+923313988471"
        user.staff_profile.save()
        for fmt in ["+923313988471", "923313988471", "0331 3988471", "+92 331 3988471"]:
            self.assertEqual(find_profile_by_phone(fmt).user, user, f"failed for {fmt}")

    def test_find_profile_none_for_unknown(self):
        self.assertIsNone(find_profile_by_phone("+10000000000"))


class ResetCodeModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("u", password="x")

    def test_valid_code(self):
        code = PhoneResetCode.objects.create(user=self.user, code="123456")
        self.assertTrue(code.is_valid())

    def test_expired_code_invalid(self):
        code = PhoneResetCode.objects.create(user=self.user, code="123456")
        code.expires_at = timezone.now() - timedelta(minutes=1)
        code.save()
        self.assertFalse(code.is_valid())

    def test_used_code_invalid(self):
        code = PhoneResetCode.objects.create(user=self.user, code="123456", used=True)
        self.assertFalse(code.is_valid())


class ResetFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            "admin2", password="OldPass!123", email="a@example.com"
        )
        self.user.staff_profile.phone = "+923313988471"
        self.user.staff_profile.save()
        self.request_url = reverse("admin_password_reset")
        self.verify_url = reverse("phone_reset_verify")

    def test_request_generates_code_and_redirects(self):
        res = self.client.post(self.request_url, {"phone": "0331 3988471"})
        self.assertEqual(res.status_code, 302)
        self.assertTrue(PhoneResetCode.objects.filter(user=self.user, used=False).exists())

    def test_unknown_phone_shows_error_no_code(self):
        res = self.client.post(self.request_url, {"phone": "+10000000000"})
        self.assertEqual(res.status_code, 200)  # re-renders the form
        self.assertContains(res, "No active account")
        self.assertEqual(PhoneResetCode.objects.count(), 0)

    def test_full_reset_changes_password(self):
        self.client.post(self.request_url, {"phone": "+923313988471"})
        code = PhoneResetCode.objects.filter(user=self.user).latest("created_at").code
        res = self.client.post(
            self.verify_url,
            {"code": code, "new_password1": "BrandNew!456", "new_password2": "BrandNew!456"},
        )
        self.assertEqual(res.status_code, 302)
        self.assertIsNotNone(authenticate(username="admin2", password="BrandNew!456"))
        self.assertTrue(PhoneResetCode.objects.get(code=code).used)

    def test_wrong_code_rejected(self):
        self.client.post(self.request_url, {"phone": "+923313988471"})
        res = self.client.post(
            self.verify_url,
            {"code": "000000", "new_password1": "BrandNew!456", "new_password2": "BrandNew!456"},
        )
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Incorrect code")
        self.assertIsNone(authenticate(username="admin2", password="BrandNew!456"))

    def test_mismatched_passwords_rejected(self):
        self.client.post(self.request_url, {"phone": "+923313988471"})
        code = PhoneResetCode.objects.filter(user=self.user).latest("created_at").code
        res = self.client.post(
            self.verify_url,
            {"code": code, "new_password1": "BrandNew!456", "new_password2": "Different!789"},
        )
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "two password fields")

    def test_verify_without_request_redirects(self):
        res = self.client.get(self.verify_url)
        self.assertEqual(res.status_code, 302)
