from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from services.selectors import services_recommended_for_user


class UserRecommendationsView(LoginRequiredMixin, TemplateView):
    template_name = "users/recommendations.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx["recommended_services"] = services_recommended_for_user(user)
        return ctx
