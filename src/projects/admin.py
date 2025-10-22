from django.contrib import admin

from projects.models import Offer, Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):

    model = Project
    list_display = [
        "title",
        "category",
        "customer",
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
                    "customer",
                    "title",
                    "category",
                    "is_active",
                ]
            },
        ),
        (
            "Описание",
            {
                "fields": [
                    "description",
                ]
            },
        ),
        (
            "Стоимость",
            {
                "fields": [
                    "price",
                    "is_higher_price_allowed",
                    "max_price",
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


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):

    model = Offer
    list_display = ["id", "project", "candidate", "status"]
    readonly_fields = [
        "created",
        "updated",
    ]
