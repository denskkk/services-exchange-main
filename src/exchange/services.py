from django.contrib.contenttypes.models import ContentType
from orders.models import Order
from users.models import CustomUser

from exchange.models import Chat, Message


def chat_get_or_create(sender: CustomUser, recipient: CustomUser, topic: Order) -> Chat:
    queryset = Chat.objects.filter(
        messages__recipient=recipient, messages__sender=sender
    )

    if topic is not None:
        queryset = Chat.objects.filter(
            topic_ct=ContentType.objects.get_for_model(topic), topic_id=topic.pk
        )

    chat = queryset.first()
    if chat is None:
        if topic:
            chat = Chat.objects.create(
                topic_ct=ContentType.objects.get_for_model(topic), topic_id=topic.pk
            )
        else:
            chat = Chat.objects.create()

    chat.save()
    return chat


def message_create(
    sender: CustomUser,
    recipient: CustomUser,
    topic: Order | None,
    text: str,
    file=None,
) -> Message:
    """Создает сообщение, при необходимости создаёт новый чат."""
    chat = chat_get_or_create(sender=sender, recipient=recipient, topic=topic)
    message = Message.objects.create(
        chat=chat,
        sender=sender,
        recipient=recipient,
        text=text,
        file=file,
    )
    message.save()
    return message
