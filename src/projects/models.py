from django.db import models
from exchange.models import Category
from users.models import CustomUser


class Project(models.Model):
    """Проект, предлагаемый пользователем для реализации другими пользователями."""

    customer = models.ForeignKey(
        verbose_name="замовник проєкту",
        help_text="Користувач, який пропонує даний проєкт для реалізації",
        to=CustomUser,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="projects",
    )
    title = models.CharField(
        verbose_name="назва",
        max_length=70,
        null=False,
        blank=False,
    )
    category = models.ForeignKey(
        verbose_name="рубрика",
        help_text="Категорія, в якій буде розміщено проєкт",
        to=Category,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="projects",
    )
    description = models.TextField(
        verbose_name="детальний опис завдання",
        help_text="Опишіть, що саме вам потрібно, в якому обсязі і за який термін.",
        max_length=5200,
        null=False,
        blank=False,
    )
    price = models.IntegerField(
        verbose_name="ціна не більше",
        help_text="Ваш бюджет в грн.",
        null=False,
        blank=False,
    )
    is_higher_price_allowed = models.BooleanField(
        verbose_name="Готовий розглянути пропозиції з ціною вище, якщо рівень виконавця буде вищим",
        default=False,
    )
    max_price = models.IntegerField(
        verbose_name="максимальна ціна",
        help_text="Максимальна ціна у разі високого рівня виконавця.",
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(
        verbose_name="проєкт активний",
        help_text="Зніміть галочку, щоб виключити проєкт з каталогу, не видаляючи його.",
        default=True,
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
        verbose_name = "проєкт"
        verbose_name_plural = "проєкти"

    def __str__(self):
        return self.title


class Offer(models.Model):
    """Предложение кандидатом своей послуги по выполнению проєкта замовника."""

    STATUS_CHOICES = (
        ("created", "Створено кандидатом"),
        ("declined", "Відхилено замовником"),
        ("cancelled", "Скасовано кандидатом"),
        ("accepted", "Прийнято замовником"),
    )

    project = models.ForeignKey(
        verbose_name="проєкт",
        to=Project,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="offers",
    )
    candidate = models.ForeignKey(
        verbose_name="кандидат на выполнение проєкта",
        help_text="Пользователь, который предлагает свои послуги для реализации проєкта.",
        to=CustomUser,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="offers",
    )
    comment = models.TextField(
        verbose_name="комментарий",
        help_text="Коментар кандидата для замовника касательно проєкта.",
        max_length=500,
        null=True,
        blank=True,
    )
    status = models.CharField(
        verbose_name="статус предложения",
        choices=STATUS_CHOICES,
        default="created",
        max_length=32,
    )
    is_cancelled = models.BooleanField(
        verbose_name="скасованоо",
        help_text="Предложение скасованоо или отклонено.",
        default=False,
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
        verbose_name = "предложение"
        verbose_name_plural = "предложения"
