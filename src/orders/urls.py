from django.urls import path

from orders.views import (
    OrderDetailView,
    OrderListView,
    order_service_create_view,
    order_set_status_view,
)

app_name = "orders"
urlpatterns = [
    path("", OrderListView.as_view(), name="list"),
    path("<int:pk>/", OrderDetailView.as_view(), name="detail"),
    path("create/service/", order_service_create_view, name="create_service"),
    path("set_status/<int:order_id>/", order_set_status_view, name="set_status"),
]
