from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = (
    [
        path("__debug__/", include("debug_toolbar.urls")),
        path("admin/", admin.site.urls),
        path("accounts/", include("allauth.urls")),
        path("", include("core.urls")),
        path("users/", include("users.urls")),
        path("exchange/", include("exchange.urls")),
        path("services/", include("services.urls")),
        path("projects/", include("projects.urls")),
        path("orders/", include("orders.urls")),
    ]
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)


# Configure Admin panel titles
admin.site.site_header = "Биржа Услуг – Администрирование"
admin.site.site_title = "Биржа Услуг – Админка"
admin.site.index_title = "Биржа Услуг – Админка"
