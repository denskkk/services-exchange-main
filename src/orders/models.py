from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from users.models import CustomUser


class Order(models.Model):
    """Заказ послуги или проєкта."""

    STATUS_CHOICES = (
        ("created", "Розміщено замовником"),
        ("in_progress", "В роботі у виконавця"),
        ("cancelled_by_customer", "Скасовано замовником"),
        ("rejected_by_provider", "Відхилено виконавцем"),
        ("submitted_by_provider", "Здано виконавцем"),
        ("returned_by_customer", "Повернуто замовником на доопрацювання"),
        ("accepted_by_customer", "Прийнято замовником"),
        ("paid", "Оплачено"),
        ("completed", "Завершено"),
    )

    customer = models.ForeignKey(
        CustomUser,
        verbose_name="замовник",
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name="orders_as_customer",
    )
    provider = models.ForeignKey(
        CustomUser,
        verbose_name="виконавець",
        on_delete=models.CASCADE,
        blank=False,
        null=False,
        related_name="orders_as_provider",
    )
    #
    # item - предмет замовленняа. Это может быть Project или Service.
    #
    item_ct = models.ForeignKey(
        ContentType,
        blank=False,
        null=False,
        related_name="item_obj",
        on_delete=models.CASCADE,
    )
    item_id = models.PositiveIntegerField(
        null=False,
        blank=False,
    )
    item = GenericForeignKey(
        ct_field="item_ct",
        fk_field="item_id",
    )
    price = models.IntegerField(
        verbose_name="вартість",
        help_text="Вартість замовлення в грн.",
        null=False,
        blank=False,
    )
    status = models.CharField(
        verbose_name="статус замовлення",
        choices=STATUS_CHOICES,
        default="created",
        max_length=32,
    )
    comment = models.TextField(
        verbose_name="коментар до замовлення",
        max_length=1500,
        blank=True,
        null=True,
    )
    is_completed = models.BooleanField(
        verbose_name="завершено",
        default=False,
    )
    is_paid = models.BooleanField(
        verbose_name="оплачено",
        default=False,
    )
    is_cancelled = models.BooleanField(
        verbose_name="скасовано",
        default=False,
    )
    created = models.DateTimeField(
        verbose_name="створено",
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        verbose_name="оновлено",
        auto_now=True,
    )

    class Meta:
        ordering = ["-created"]
        verbose_name = "замовлення"
        verbose_name_plural = "замовлення"

    def __str__(self):
        return f"Заказ №{self.id}"
