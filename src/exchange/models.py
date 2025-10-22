from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from users.models import CustomUser


class Category(models.Model):
    """Категорія послуги или проєкта."""

    title = models.CharField(
        verbose_name="назва",
        max_length=70,
    )
    parent = models.ForeignKey(
        verbose_name="батьківська категорія",
        to="Category",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subcategories",
    )

    class Meta:
        ordering = ["title"]
        verbose_name = "категорія"
        verbose_name_plural = "категорії"

    def __str__(self):
        title = self.title
        parent = self.parent
        while parent:
            title = f"{parent.title} / {title}"
            parent = parent.parent
        return title


class CategoryProposal(models.Model):
    """Запропонована користувачем категорія (на модерацію)."""

    class Status(models.TextChoices):
        PENDING = "pending", "прийнято на модерацію"
        APPROVED = "approved", "схвалено"
        REJECTED = "rejected", "відхилено"

    title = models.CharField("назва", max_length=70)
    parent = models.ForeignKey(
        to=Category, verbose_name="батьківська категорія", null=True, blank=True, on_delete=models.SET_NULL
    )
    description = models.TextField("опис/обґрунтування", max_length=1000, blank=True)
    user = models.ForeignKey(CustomUser, verbose_name="користувач", on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = "запропонована категорія"
        verbose_name_plural = "запропоновані категорії"

    def __str__(self) -> str:
        return f"{self.title} ({self.get_status_display()})"


class Chat(models.Model):
    """Чат объединяет повідомлення и topic – модель БД, с которой связан чат (замовлення, проєкт...)"""

    topic_ct = models.ForeignKey(
        ContentType,
        blank=True,
        null=True,
        related_name="topic_obj",
        on_delete=models.CASCADE,
    )
    topic_id = models.PositiveIntegerField(
        null=True,
        blank=True,
    )
    topic = GenericForeignKey(
        ct_field="topic_ct",
        fk_field="topic_id",
    )
    latest_message = models.OneToOneField(
        to="Message",
        verbose_name="Останнє повідомлення",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="latest_in_chat",
    )
    created = models.DateTimeField(
        verbose_name="створено",
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        verbose_name="змінено",
        auto_now=True,
    )

    class Meta:
        ordering = ["-created"]
        verbose_name = "чат"
        verbose_name_plural = "чати"

    def __str__(self):
        return f"Чат {self.pk}"


class Message(models.Model):
    """Повідомлення в чате."""

    chat = models.ForeignKey(
        to=Chat,
        verbose_name="чат",
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name="messages",
    )
    sender = models.ForeignKey(
        to=CustomUser,
        verbose_name="відправник",
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name="messages_sent",
    )
    recipient = models.ForeignKey(
        to=CustomUser,
        verbose_name="отримувач",
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name="messages_received",
    )
    text = models.TextField(
        verbose_name="Текст повідомлення",
        max_length=1500,
        blank=False,
        null=False,
    )
    file = models.FileField(
        verbose_name="вложение",
        help_text="Файл, прилагаемый к сообщению.",
        upload_to="attachments/",
        blank=True,
        null=True,
    )
    is_read = models.BooleanField(
        verbose_name="прочитано",
        help_text="Повідомлення прочитано получателем.",
        default=False,
    )
    created = models.DateTimeField(
        verbose_name="створеноо",
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        verbose_name="зміненоо",
        auto_now=True,
    )

    class Meta:
        ordering = ["-created"]
        verbose_name = "cообщение"
        verbose_name_plural = "повідомлення"

    def __str__(self):
        return (
            f"Повідомлення {self.pk} от {self.sender.username} к {self.recipient.username}"
        )
