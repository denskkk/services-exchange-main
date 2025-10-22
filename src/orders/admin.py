from django.contrib import admin

from orders.models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    model = Order
    list_display = [
        "id",
        "customer",
        "provider",
        "item",
        "status",
        "is_paid",
        "price",
    ]
    list_filter = [
        "status",
        "is_paid",
    ]
    readonly_fields = [
        "created",
        "updated",
    ]
    fieldsets = [
        (
            "Заказчик и исполнитель",
            {
                "fields": [
                    "customer",
                    "provider",
                ]
            },
        ),
        (
            "Подробности заказа",
            {
                "fields": [
                    "item_ct",
                    "item_id",
                    "price",
                    "comment",
                ]
            },
        ),
        (
            "Статус",
            {
                "fields": [
                    "status",
                    "is_completed",
                    "is_paid",
                    "is_cancelled",
                ]
            },
        ),
        (
            "Время создания и изменения",
            {
                "fields": [
                    "created",
                    "updated",
                ]
            },
        ),
    ]
