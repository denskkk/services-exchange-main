from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from orders.selectors import order_get_by_id
from users.selectors import user_get_by_id

from exchange.forms import MessageCreateForm, CategoryProposalForm
from exchange.models import Category, CategoryProposal
from exchange.selectors import category_list
from exchange.services import message_create


def set_user_mode(request):
    """
    Устанавливает режим пользователя - покупатель или продавец, и редиректит на
    указанную страницу.

    Пример использования в шаблоне:
        <a href="{% url 'exchange:set_user_mode' %}?mode=buyer&redirect_to={{ request.path }}">
    """
    mode = request.GET.get("mode", "buyer")
    redirect_to = request.GET.get("redirect_to", "/")

    request.session["user_mode"] = mode

    return redirect(redirect_to)


class CategoryListView(ListView):
    model = Category
    template_name = "exchange/category_list.html"

    def get_queryset(self):
        return category_list()


@login_required
def propose_category_view(request: HttpRequest) -> HttpResponse:
    """Страница отправки предложения новой категории."""
    if request.method == "POST":
        form = CategoryProposalForm(request.POST)
        if form.is_valid():
            proposal: CategoryProposal = form.save(commit=False)
            proposal.user = request.user
            proposal.status = CategoryProposal.Status.PENDING
            proposal.save()
            return render(request, "exchange/category_proposal_success.html", {"proposal": proposal})
    else:
        form = CategoryProposalForm()

    return render(request, "exchange/category_proposal_form.html", {"form": form})


@login_required
@require_POST
def message_create_view(request: HttpRequest) -> HttpResponse:
    """
    Отправляет повідомлення в чат, связанный с замовленняом. Пока чати есть только в замовленняах.

    TODO: make it work not only with orders
    """
    form = MessageCreateForm(request.POST, request.FILES)

    if form.is_valid():
        data = form.cleaned_data
        topic_ct = data["topic_ct"]
        topic_id = data["topic_id"]
        order = order_get_by_id(order_id=topic_id)
        sender = request.user
        recipient_id = data["recipient_id"]
        recipient = user_get_by_id(recipient_id)
        text = data["text"]
        file = request.FILES.get("file", None)

        message = message_create(
            sender=sender, recipient=recipient, topic=order, text=text, file=file
        )
        return redirect(
            reverse_lazy("orders:detail", kwargs={"pk": topic_id})
            + "#message_"
            + str(message.pk)
        )
    return redirect(reverse_lazy("orders:list"))
