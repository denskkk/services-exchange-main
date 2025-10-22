from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)
from django_project.rds import redis
from exchange.selectors import (
    category_get_by_id,
    category_list_only_available,
    category_list_only_with_services,
)
from exchange.models import Category, CategoryProposal
from users.models import Action
from users.services import action_create

from services.models import Service
from services.forms import ServiceCreateForm
from services.selectors import service_get_by_id, service_list


class ServiceListView(ListView):
    model = Service
    template_name = "services/service_list.html"

    def get_queryset(self):
        category_id = self.request.GET.get("category_id", None)
        search = self.request.GET.get("search", None)
        return service_list(category_id=category_id, search=search)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        category_id = self.request.GET.get("category_id", None)

        if category_id is not None:
            category = category_get_by_id(category_id)
            context["category"] = category

        context["categories"] = category_list_only_with_services()
        context["search"] = self.request.GET.get("search", None)
        return context


class ServiceMyListView(LoginRequiredMixin, ListView):
    """Послуги залогиненного пользователя – страница "Мої послуги"."""

    model = Service
    template_name = "services/service_my_list.html"

    def get_queryset(self):
        return service_list(provider_id=self.request.user.id)


class ServiceDetailView(DetailView):
    model = Service
    template_name = "services/service_detail.html"

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)

        if pk is None:
            raise AttributeError(
                "Detail view %s must be called with an object "
                "pk in the URLconf." % self.__class__.__name__
            )

        return service_get_by_id(service_id=pk)

    def get(self, request, *args, **kwargs):
        """
        Для аутентифицированного пользователя создадим действие, чтобы сохранить историю просмотра.
        Перегляды пользователем своих услуг фиксировать не будем.
        """
        service = self.get_object()
        if service is None:
            raise Http404

        if self.request.user.is_authenticated and (
            service.provider != self.request.user
        ):
            action_create(
                user=self.request.user,
                verb=Action.VIEW_SERVICE,
                target=service,
            )

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = self.get_object()
        if service is not None:
            context["total_views"] = redis.incr(f"service:{service.pk}:views")
        return context


class ServiceCreateView(LoginRequiredMixin, CreateView):
    model = Service
    template_name = "services/service_create.html"
    form_class = ServiceCreateForm

    def get_form(self, form_class=None):
        """Оставляем в списке формы только категорії, доступные для назначения услуге."""
        form = super().get_form(form_class)
        form.fields["category"].queryset = category_list_only_available()
        return form

    def form_valid(self, form):
        """Set logged in user as `provider` of new Service."""
        service = form.save(commit=False)
        service.provider = self.request.user
        service.save()
        # If user proposed a new category title, create a Category immediately
        proposed = form.cleaned_data.get("proposed_category_title")
        if proposed:
            parent = form.cleaned_data.get("category")
            new_cat, _ = Category.objects.get_or_create(title=proposed, parent=parent)
            service.category = new_cat
            service.save(update_fields=["category"]) 
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("services:detail", kwargs={"pk": self.object.pk})


class ServiceUpdateView(
    LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView
):
    model = Service
    fields = [
        "title",
        "category",
        "is_active",
        "image",
        "description",
        "requirements",
        "price",
        "term",
        "options",
        "portfolio_url",
    ]
    template_name = "services/service_update.html"
    success_message = "Сведения об услуге успешно зміненоы."

    def test_func(self):
        """Only allow user to update own service."""
        user = self.get_object().provider
        return user == self.request.user

    def get_success_url(self):
        return reverse_lazy("services:update", kwargs={"pk": self.get_object().pk})


class ServiceDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Service
    template_name = "services/service_delete.html"
    success_url = reverse_lazy("services:my_list")

    def test_func(self):
        """Only allow owner of the service to delete it."""
        service = self.get_object()
        return service.provider == self.request.user
