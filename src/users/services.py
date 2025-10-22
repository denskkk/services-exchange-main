import datetime

from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from projects.models import Project
from services.models import Service

from users.models import Action, CustomUser
from users.selectors import user_get_by_id


def action_create(user, verb: str, target=None) -> None:
    """
    Создает указанное действие, если не было аналогичных действий в течение 10 минут.
    Для 'verb' использовать константы из класса Action, например `Action.VIEW_PROJECT`.
    """
    # Выбираем аналогичные действия пользователя за последние десять минут
    now = timezone.now()
    last_ten_minutes = now - datetime.timedelta(seconds=600)
    similar_actions = Action.objects.filter(
        user_id=user.id, verb=verb, created__gte=last_ten_minutes
    )

    if target:
        target_ct = ContentType.objects.get_for_model(target)
        similar_actions = similar_actions.filter(
            target_ct=target_ct, target_id=target.id
        )

    if not similar_actions:
        Action.objects.create(user=user, verb=verb, target=target)


def user_pay_from_balance(user_id: int, item: Project | Service) -> bool:
    """Уменьшает баланс пользователя на сайте на размер стоимости услуги или проекта,
    если на балансе достаточно средств."""
    user = user_get_by_id(user_id=user_id)
    if user is None or user.balance < item.price:
        return False

    user.balance -= item.price
    user.save()
    return True


def user_refund_to_balance(user: CustomUser, item: Project | Service) -> None:
    """Возвращает на баланс пользователя на сайте стоимость услуги или проекта
    (в случае отмены или отклонения заказа)."""
    user.balance += item.price
    user.save()


def user_payment_to_balance(user: CustomUser, item: Project | Service) -> None:
    """Зачисляет на баланс исполнителя оплату за выполненную услугу или проект
    (когда работа принята заказчиком)."""
    user.balance += item.price
    user.save()
