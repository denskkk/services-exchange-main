from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView
from exchange.selectors import message_list_for_topic
from services.selectors import service_get_by_id
from users.selectors import action_list_for_order
from users.services import user_pay_from_balance

from orders.forms import CreateServiceOrderForm, OrderChangeStatusForm
from orders.models import Order
from orders.selectors import (
    order_get_by_id,
    order_list_as_customer,
    order_list_as_provider,
)
from orders.services import order_create, order_set_status


@require_POST
@login_required
def order_service_create_view(request: HttpRequest) -> HttpResponse:
    """Вид размещения замовленняа на услугу."""
    form = CreateServiceOrderForm(request.POST)

    if form.is_valid():
        data = form.cleaned_data
        service_id = data["service_id"]
        service = service_get_by_id(service_id=service_id)

        if not service:
            raise Http404

        is_paid = user_pay_from_balance(user_id=request.user.pk, item=service)
        if not is_paid:
            messages.warning(
                request,
                "На вашому балансі недостатньо коштів для оплаты послуги. "
                "Пополните баланс, и попробуйте еще раз.",
                extra_tags="warning",
            )
            return redirect(reverse_lazy("services:detail", kwargs={"pk": service.pk}))

        order = order_create(
            customer=request.user,
            provider=service.provider,
            item=service,
            price=service.price,
        )
        messages.success(request, "Заказ был успешно створено.")
        return redirect(reverse_lazy("orders:detail", kwargs={"pk": order.pk}))

    return redirect(reverse_lazy("services:list"))


@require_POST
@login_required()
def order_set_status_view(request: HttpRequest, order_id: int) -> HttpResponse:
    """Вид зміненоия статуса замовленняа."""
    order = order_get_by_id(order_id=order_id)
    if order is None:
        raise Http404

    if (request.user != order.customer) and (request.user != order.provider):
        raise PermissionDenied(
            "Статус замовленняа могут менять только замовник или виконавець замовленняа"
        )

    form = OrderChangeStatusForm(request.POST)
    if form.is_valid():
        data = form.cleaned_data
        new_status = data["new_status"]

        order_set_status(order=order, new_status=new_status, actor=request.user)

        if order.status == new_status:
            messages.success(request, "Статус замовленняа успешно изменён.")
        else:
            messages.warning(
                request,
                "Не удалось изменить статус замовлення. Попробуйте ещё раз!",
                extra_tags="warning",
            )

    return redirect(reverse_lazy("orders:detail", kwargs={"pk": order.pk}))


class OrderDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Order
    template_name = "orders/order_detail.html"

    def test_func(self):
        """Только замовник или виконавець могут просматривать замовлення"""
        order = self.get_object()
        return (order.customer == self.request.user) or (
            order.provider == self.request.user
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        order = self.get_object()
        context["actions"] = action_list_for_order(order_id=order.pk)
        context["chat_messages"] = message_list_for_topic(topic=order)

        return context


class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "orders/order_list.html"

    def get_queryset(self):
        """Фильтруем замовлення в зависимиости от режима пользователя – покупатель или продавец."""
        user_mode = self.request.session.get("user_mode")
        if user_mode == "buyer":
            queryset = order_list_as_customer(user_id=self.request.user.pk)
        else:
            queryset = order_list_as_provider(user_id=self.request.user.pk)
        return queryset
