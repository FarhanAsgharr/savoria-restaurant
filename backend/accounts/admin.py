"""
Admin integration: add the WhatsApp phone field onto the User edit page so
staff can register the number their reset codes are sent to.
"""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import StaffProfile

User = get_user_model()


class StaffProfileInline(admin.StackedInline):
    model = StaffProfile
    can_delete = False
    verbose_name = "WhatsApp / phone"
    verbose_name_plural = "WhatsApp / phone"


class UserAdmin(BaseUserAdmin):
    inlines = (StaffProfileInline,)
    list_display = BaseUserAdmin.list_display + ("get_phone",)

    @admin.display(description="WhatsApp")
    def get_phone(self, obj):
        profile = getattr(obj, "staff_profile", None)
        return profile.phone if profile and profile.phone else "—"


# Replace the default User admin with our phone-aware one.
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
