from celery import shared_task

from users.models import CustomUser


@shared_task
def user_add_to_balance(user_id: int, amount: int, card_number: int):
    """Здесь предполагается обращение к внешнему сервису для пополнения баланса
    пользователя с карты. Пока в демонстрационных целях баланс просто увеличивается
    на указанную сумму."""
    user = CustomUser.objects.filter(id=user_id).first()

    if user is None:
        return

    print(f"Adding {amount} to {user} from card #{card_number}...")
    user.balance += amount
    user.save()
