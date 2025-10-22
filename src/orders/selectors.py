from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, QuerySet
from projects.models import Project

from orders.models import Order


def order_list(user_id: int) -> QuerySet:
    """Выбирает заказы, где пользователь с user_id заказчик или исполнитель."""
    orders = Order.objects.filter(Q(customer_id=user_id) | Q(provider_id=user_id)).all()
    return orders


def order_list_as_customer(user_id: int) -> QuerySet:
    return Order.objects.filter(customer_id=user_id).all()


def order_list_as_provider(user_id: int) -> QuerySet:
    return Order.objects.filter(provider_id=user_id).all()


def order_get_by_id(order_id: int) -> Order | None:
    return Order.objects.filter(id=order_id).first()


def order_get_by_project_id(project_id: int, user) -> Order | None:
    """Вовзращает заказ указанного проекта, где пользователь является заказчиком или исполнителем."""
    return (
        Order.objects.filter(
            item_ct=ContentType.objects.get_for_model(Project), item_id=project_id
        )
        .filter(Q(customer=user) | Q(provider=user))
        .first()
    )
