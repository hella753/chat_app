from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from user.models import User


@admin.register(User)
class UserAdmin(UserAdmin):
    add_fieldsets = (
        (None, {
            "fields": ("username",
                       "email",
                       "first_name",
                       "last_name",
                       "password1",
                       "password2"),
        }),
    )
    fieldsets = UserAdmin.fieldsets + (
        ("Profile Info", {"fields": (
            "image",
            "friends",
            "friend_requests",
        )}),
    )

    list_display = (
        "first_name",
        "last_name",
        "username",
        "email",
        "is_active",
    )
