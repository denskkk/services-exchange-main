from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
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
    category_list_only_with_projects,
)
from orders.selectors import order_get_by_project_id
from users.models import Action
from users.services import action_create

from projects.forms import OfferCreateForm, OfferSetStatusForm
from projects.models import Project
from projects.selectors import (
    offer_get_by_id,
    offer_list,
    project_get_by_id,
    project_list,
)
from projects.services import offer_create, offer_set_status


class ProjectListView(ListView):
    model = Project
    template_name = "projects/project_list.html"

    def get_queryset(self):
        category_id = self.request.GET.get("category_id", None)
        search = self.request.GET.get("search", None)
        return project_list(
            category_id=category_id, exclude_with_orders=True, search=search
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        category_id = self.request.GET.get("category_id", None)

        if category_id is not None:
            category = category_get_by_id(category_id)
            context["category"] = category

        context["categories"] = category_list_only_with_projects()
        context["search"] = self.request.GET.get("search", None)
        return context


class ProjectMyListView(LoginRequiredMixin, ListView):
    """Проекты залогиненного пользователя – страница "Мої проєкти"."""

    model = Project
    template_name = "projects/project_my_list.html"

    def get_queryset(self):
        return project_list(customer_id=self.request.user.id)


class ProjectDetailView(DetailView):
    model = Project
    template_name = "projects/project_detail.html"

    def get_object(self, queryset=None):
        pk = self.kwargs.get(self.pk_url_kwarg)

        if pk is None:
            raise AttributeError(
                "Detail view %s must be called with an object "
                "pk in the URLconf." % self.__class__.__name__
            )

        return project_get_by_id(project_id=pk)

    def get(self, request, *args, **kwargs):
        """
        Для аутентифицированного пользователя создадим действие, чтобы сохранить историю просмотра.
        Перегляды пользователем своих проєктов фиксировать не будем.
        """
        project = self.get_object()
        if project is None:
            raise Http404

        if self.request.user.is_authenticated and (
            project.customer != self.request.user
        ):
            action_create(
                user=self.request.user,
                verb=Action.VIEW_PROJECT,
                target=project,
            )

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        project = self.get_object()

        candidate = None
        if self.request.user.is_authenticated and (
            self.request.user != project.customer
        ):
            candidate = self.request.user

        context["offers"] = offer_list(project_id=project.pk, candidate=candidate)

        user = None
        if self.request.user.is_authenticated:
            user = self.request.user
        context["order"] = order_get_by_project_id(project_id=project.pk, user=user)

        context["total_views"] = redis.incr(f"project:{project.pk}:views")
        return context


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    template_name = "projects/project_create.html"
    fields = [
        "title",
        "category",
        "description",
        "price",
        "is_higher_price_allowed",
        "max_price",
    ]

    def get_form(self, form_class=None):
        """Оставляем в списке формы только категорії, доступные для назначения услуге."""
        form = super().get_form(form_class)
        form.fields["category"].queryset = category_list_only_available()
        return form

    def form_valid(self, form):
        """Set logged in user as `customer` of new Project."""
        service = form.save(commit=False)
        service.customer = self.request.user
        service.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("projects:detail", kwargs={"pk": self.object.pk})


class ProjectUpdateView(
    LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView
):
    model = Project
    fields = [
        "title",
        "category",
        "is_active",
        "description",
        "price",
        "is_higher_price_allowed",
        "max_price",
    ]
    template_name = "projects/project_update.html"
    success_message = "Сведения о проєкте успешно зміненоы."

    def test_func(self):
        """Only allow user to update own project."""
        user = self.get_object().customer
        return user == self.request.user

    def get_success_url(self):
        return reverse_lazy("projects:update", kwargs={"pk": self.get_object().pk})


class ProjectDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Project
    template_name = "projects/project_delete.html"
    success_url = reverse_lazy("projects:my_list")

    def test_func(self):
        """Only allow owner of the project to delete it."""
        project = self.get_object()
        return project.customer == self.request.user


@require_POST
@login_required
def offer_create_view(request: HttpRequest) -> HttpResponse:
    form = OfferCreateForm(request.POST)

    if form.is_valid():
        data = form.cleaned_data
        project_id = data["project_id"]
        project = project_get_by_id(project_id=project_id)

        if not project:
            raise Http404

        if offer_create(project=project, candidate=request.user):
            messages.success(request, "Вы успешно подали заявку на выполнение проєкта!")
        else:
            messages.warning(
                request,
                "Не удалось разместить вашу заявку на выполнение проєкта.",
                extra_tags="warning",
            )
        return redirect(reverse_lazy("projects:detail", kwargs={"pk": project.pk}))

    return redirect(reverse_lazy("projects:list"))


@require_POST
@login_required
def offer_set_status_view(request: HttpRequest, offer_id: int) -> HttpResponse:
    offer = offer_get_by_id(offer_id)
    if offer is None:
        raise Http404

    if (request.user != offer.candidate) and (request.user != offer.project.customer):
        raise PermissionDenied(
            "Статус предложения могут менять только кандидат или замовник проєкту."
        )

    form = OfferSetStatusForm(request.POST)
    if form.is_valid():
        data = form.cleaned_data
        new_status = data["new_status"]

        offer_set_status(offer=offer, new_status=new_status, actor=request.user)

        if offer.status == new_status:
            messages.success(request, "Статус предложения успешно изменён.")
        else:
            messages.warning(
                request,
                "Не удалось изменить статус предложения. Попробуйте ещё раз!",
                extra_tags="warning",
            )

    return redirect(reverse_lazy("projects:detail", kwargs={"pk": offer.project.pk}))
