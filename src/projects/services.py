from orders.services import order_create
from users.models import CustomUser
from users.services import user_pay_from_balance

from projects.models import Offer, Project


def offer_create(
    project: Project, candidate: CustomUser, comment: str | None = None
) -> Offer | None:
    """Создаёт предложение от кандидата на выполнение проекта, если от этого
    кандидата ещё нет предложений на данный проект."""
    if Offer.objects.filter(project=project, candidate=candidate).count():
        return None

    offer = Offer(project=project, candidate=candidate, comment=comment)
    offer.save()
    return offer


def offer_set_status(offer: Offer, new_status: str, actor: CustomUser) -> None:
    """Изменяет статус предложения на указанный (если это возможно).
    В случае установки статуса `accepted`, также создаёт соответствующий заказ."""
    match new_status:
        case "cancelled":
            if (offer.status == "created") and (offer.candidate == actor):
                offer.status = "cancelled"
                offer.is_cancelled = True
        case "declined":
            if (offer.status == "created") and (offer.project.customer == actor):
                offer.status = "declined"
                offer.is_cancelled = True
        case "accepted":
            if (offer.status == "created") and (offer.project.customer == actor):
                is_paid = user_pay_from_balance(
                    user_id=offer.project.customer.pk, item=offer.project
                )
                if not is_paid:
                    return

                offer.status = "accepted"
                # Cancel all other offers for the same project
                other_offers = (
                    Offer.objects.filter(project=offer.project, is_cancelled=False)
                    .exclude(id=offer.pk)
                    .all()
                )
                other_offers.update(is_cancelled=True, status="declined")
                # Помечаем проект как "не активный", т.к. на него уже будет создан заказ.
                offer.project.is_active = False
                offer.project.save()
                # Create order for this project
                order_create(
                    customer=offer.project.customer,
                    provider=offer.candidate,
                    item=offer.project,
                    price=offer.project.price,
                )
        case _:
            return None
    offer.save()
