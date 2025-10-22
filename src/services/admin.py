from django.contrib import admin

from services.models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):

    model = Service
    list_display = [
        "title",
        "category",
        "price",
        "is_active",
        "provider",
    ]
    readonly_fields = [
        "created",
        "updated",
    ]
    fieldsets = [
        (
            "Основные",
            {
                "fields": [
                    "provider",
                    "title",
                    "category",
                    "image",
                    "is_active",
                ]
            },
        ),
        (
            "Описание",
            {
                "fields": [
                    "description",
                    "requirements",
                ]
            },
        ),
        (
            "Стоимость",
            {
                "fields": [
                    "price",
                    "term",
                ]
            },
        ),
        (
            "Дополнительно",
            {
                "fields": [
                    "options",
                    "portfolio_url",
                ]
            },
        ),
        (
            "Временные метки",
            {
                "fields": [
                    "created",
                    "updated",
                ]
            },
        ),
    ]
