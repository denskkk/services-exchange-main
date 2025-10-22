from django.db import models
from exchange.models import Category
from users.models import CustomUser


class Service(models.Model):
    """Услуга, предлагаемая пользователем сайта."""

    provider = models.ForeignKey(
        verbose_name="виконавець послуги",
        help_text="Користувач, який надає дану послугу",
        to=CustomUser,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="services",
    )
    title = models.CharField(
        verbose_name="назва",
        max_length=70,
        null=False,
        blank=False,
    )
    category = models.ForeignKey(
        verbose_name="рубрика",
        help_text="Категорія, в якій буде розміщено послугу",
        to=Category,
        on_delete=models.CASCADE,
        null=False,
        blank=False,
        related_name="services",
    )
    image = models.ImageField(
        verbose_name="обкладинка",
        null=True,
        blank=True,
        upload_to="images/services/",
    )
    description = models.TextField(
        verbose_name="опис",
        help_text="Детальний опис послуги, що надається",
        max_length=1200,
        null=False,
        blank=False,
    )
    requirements = models.TextField(
        verbose_name="від покупця потрібно",
        help_text="Вкажіть що потрібно від замовника послуги. Наприклад, ТЗ, доступи тощо.",
        max_length=500,
        null=False,
        blank=False,
    )
    price = models.IntegerField(
        verbose_name="вартість",
        help_text="Вартість послуги в грн.",
        null=False,
        blank=False,
    )
    term = models.IntegerField(
        verbose_name="термін",
        help_text="Термін виконання послуги, в днях",
        null=False,
        blank=False,
    )
    options = models.TextField(
        verbose_name="додаткові послуги",
        help_text="Якщо ви пропонуєте додаткові послуги, розкажіть про них. Вкажіть назву, термін, вартість.",
        max_length=1200,
        null=True,
        blank=True,
    )
    portfolio_url = models.URLField(
        verbose_name="посилання на портфоліо",
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(
        verbose_name="послуга активна",
        help_text="Зніміть галочку, щоб виключити послугу з каталогу, не видаляючи її.",
        default=True,
    )
    created = models.DateTimeField(
        verbose_name="створена",
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        verbose_name="змінена",
        auto_now=True,
    )

    class Meta:
        ordering = ["-created"]
        verbose_name = "послуга"
        verbose_name_plural = "послуги"

    def __str__(self):
        return self.title
