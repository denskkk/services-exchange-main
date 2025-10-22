from django.views.generic import TemplateView
from exchange.selectors import category_list_only_with_services
from services.selectors import services_latest


class IndexView(TemplateView):
    template_name = "core/index.html"
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Categories that have services (popular-ish)
        ctx["service_categories"] = category_list_only_with_services()[:12]
        # Latest services
        ctx["latest_services"] = services_latest(8)
        return ctx
