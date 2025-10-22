from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import Action, CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Configures admin panel views for CustomUsers.
    """

    model = CustomUser
    list_display = [
        "username",
        "is_staff",
    ]
    # Which fields to show when editing user via admin panel:
    fieldsets = UserAdmin.fieldsets + (
        (
            "Дополнительные сведения",
            {
                "fields": (
                    "profile_image",
                    "speciality",
                    "description",
                    "skills",
                    "country",
                    "city",
                    "phone",
                    "balance",
                )
            },
        ),
    )
    # Which fields to show when creating user via admin panel:
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            None,
            {"fields": ("profile_image",)},
        ),
    )


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ["user", "verb", "target", "created"]
    list_filter = ["created"]
    search_fields = ["verb"]
