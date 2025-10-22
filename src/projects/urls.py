from django.urls import path

from projects.views import (
    ProjectCreateView,
    ProjectDeleteView,
    ProjectDetailView,
    ProjectListView,
    ProjectMyListView,
    ProjectUpdateView,
    offer_create_view,
    offer_set_status_view,
)

app_name = "projects"
urlpatterns = [
    path("", ProjectListView.as_view(), name="list"),
    path("<int:pk>/", ProjectDetailView.as_view(), name="detail"),
    path("my/", ProjectMyListView.as_view(), name="my_list"),
    path("create/", ProjectCreateView.as_view(), name="create"),
    path("update/<int:pk>/", ProjectUpdateView.as_view(), name="update"),
    path("delete/<int:pk>/", ProjectDeleteView.as_view(), name="delete"),
    path("offer/create/", offer_create_view, name="offer_create"),
    path(
        "offer/set_status/<int:offer_id>/",
        offer_set_status_view,
        name="offer_set_status",
    ),
]
