from django.urls import path

from services.views import (
    ServiceCreateView,
    ServiceDeleteView,
    ServiceDetailView,
    ServiceListView,
    ServiceMyListView,
    ServiceUpdateView,
)

app_name = "services"
urlpatterns = [
    path("", ServiceListView.as_view(), name="list"),
    path("my/", ServiceMyListView.as_view(), name="my_list"),
    path("<int:pk>/", ServiceDetailView.as_view(), name="detail"),
    path("create/", ServiceCreateView.as_view(), name="create"),
    path("update/<int:pk>/", ServiceUpdateView.as_view(), name="update"),
    path("delete/<int:pk>/", ServiceDeleteView.as_view(), name="delete"),
]
