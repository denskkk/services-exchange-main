from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from django.db import models


class CustomUser(AbstractUser):
    """
    Custom user model with additional fields.
    """

    profile_image = models.ImageField(
        verbose_name="зображення профілю",
        null=True,
        blank=True,
        upload_to="images/profiles/",
    )
    speciality = models.CharField(
        verbose_name="ви за спеціальністю",
        max_length=50,
        null=True,
        blank=True,
    )
    description = models.TextField(
        verbose_name="інформація про вас і ваш досвід",
        max_length=1200,
        null=True,
        blank=True,
    )
    skills = ArrayField(
        models.CharField(
            max_length=32,
        ),
        verbose_name="ваші навички",
        help_text="Список ваших навичок через кому",
        null=True,
        blank=True,
    )
    country = models.CharField(
        verbose_name="країна",
        max_length=64,
        null=True,
        blank=True,
    )
    city = models.CharField(
        verbose_name="місто",
        max_length=64,
        null=True,
        blank=True,
    )
    phone = models.CharField(
        verbose_name="телефон",
        help_text="Номер телефону у форматі +380(00)000-00-00",
        max_length=64,
        null=True,
        blank=True,
    )
    balance = models.DecimalField(
        verbose_name="баланс",
        max_digits=10,
        decimal_places=2,
        default=0.0,
    )

    # Onboarding questionnaire fields
    has_children = models.BooleanField(
        verbose_name="є діти",
        help_text="Позначте, якщо у вашій сім'ї є діти",
        default=False,
    )
    has_pets = models.BooleanField(
        verbose_name="є домашні тварини",
        help_text="Позначте, якщо у вас є домашні тварини",
        default=False,
    )
    HOME_TYPE_CHOICES = (
        ("apartment", "Квартира"),
        ("house", "Будинок"),
        ("other", "Інше"),
    )
    home_type = models.CharField(
        verbose_name="тип житла",
        max_length=20,
        choices=HOME_TYPE_CHOICES,
        null=True,
        blank=True,
    )
    car_owner = models.BooleanField(
        verbose_name="є власний автомобіль",
        default=False,
    )
    EMPLOYMENT_CHOICES = (
        ("employee", "Найманий працівник"),
        ("self_employed", "Самозайнятий/ФОП"),
        ("student", "Студент"),
        ("parent", "Батько/Мати в декреті"),
        ("retired", "На пенсії"),
        ("unemployed", "Тимчасово без роботи"),
    )
    employment_status = models.CharField(
        verbose_name="зайнятість",
        max_length=20,
        choices=EMPLOYMENT_CHOICES,
        null=True,
        blank=True,
    )
    prefer_online_services = models.BooleanField(
        verbose_name="надаю перевагу онлайн послугам",
        default=True,
    )
    questionnaire_completed = models.BooleanField(
        verbose_name="анкету заповнено",
        default=False,
    )

    class Meta:
        ordering = ["id"]
        verbose_name = "користувач"
        verbose_name_plural = "користувачі"

    def __str__(self):
        return self.username

    @property
    def full_name(self) -> str | None:
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def location(self) -> str | None:
        if self.country and self.city:
            return f"{self.city}, {self.country}".strip()
        elif self.city:
            return self.city.strip()
        elif self.country:
            return self.country.strip()
        return None


class Action(models.Model):
    """
    Модель для хранения "действий" пользователя, направленных на другие модели в БД ("target").

    user: користувач, совершивший действие
    verb: что было сделано; использовать константы из этой модели
    created: дата/время действия
    target_ct: модель "цели" действия
    target_id: ID связанного объекта "цели"
    target: поле для створеноия связи на основе двух предыдущих полей
    """

    VIEW_SERVICE = "просмотрена послуга"
    VIEW_PROJECT = "просмотрен проєкт"
    PLACE_ORDER = "размещен замовлення"
    RECEIVE_ORDER = "получен замовлення"  # виконавець получил замовлення
    CANCEL_ORDER = "скасовано замовлення"  # замовник отменил замовлення
    REJECT_ORDER = "отклонен замовлення"  # виконавець отказался от замовленняа
    ACCEPT_ORDER = "принят в работу замовлення"  # виконавець взял в работу замовлення
    SUBMIT_ORDER = "сдан на проверку замовлення"
    RETURN_ORDER = "возвращен на доработку замовлення"
    COMPLETE_ORDER = (
        "успешно выполнил замовлення"  # виконавець успешно сдал работу замовнику
    )
    RECEIVE_RESULT = (
        "получил результат работы по замовленняу"  # замовник получил результат работы
    )

    user = models.ForeignKey(
        verbose_name="користувач",
        to=CustomUser,
        related_name="actions",
        on_delete=models.CASCADE,
    )
    verb = models.CharField(
        verbose_name="действие",
        max_length=64,
    )
    target_ct = models.ForeignKey(
        ContentType,
        blank=True,
        null=True,
        related_name="target_obj",
        on_delete=models.CASCADE,
    )
    target_id = models.PositiveIntegerField(
        null=True,
        blank=True,
    )
    target = GenericForeignKey(
        ct_field="target_ct",
        fk_field="target_id",
    )
    created = models.DateTimeField(
        verbose_name="время события",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "действие"
        verbose_name_plural = "действия"
        ordering = ["-created"]


class DetailedQuestionnaire(models.Model):
    """Детальна анкета для підбору послуг."""

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="questionnaire",
        verbose_name="користувач",
    )

    # Склад сім'ї / побут
    household_adults = models.PositiveSmallIntegerField("Дорослих у домогосподарстві", default=1)
    household_children = models.PositiveSmallIntegerField("Дітей у домогосподарстві", default=0)
    has_infants = models.BooleanField("Є немовлята", default=False)

    # Тварини
    pets_dogs = models.BooleanField("Є собаки", default=False)
    pets_cats = models.BooleanField("Є коти", default=False)
    pets_other = models.BooleanField("Інші тварини", default=False)

    # Житло
    dwelling_type = models.CharField(
        "Тип житла",
        max_length=20,
        choices=[("apartment", "Квартира"), ("house", "Будинок"), ("other", "Інше")],
        default="apartment",
    )
    dwelling_rooms = models.PositiveSmallIntegerField("Кімнат", default=1)
    dwelling_area = models.PositiveIntegerField("Площа (кв.м)", default=40)
    has_garden = models.BooleanField("Є подвір'я/сад", default=False)

    # Транспорт
    car_owner = models.BooleanField("Є авто", default=False)
    bike_owner = models.BooleanField("Є велосипед/електросамокат", default=False)

    # Доступність/час
    availability_weekdays = models.BooleanField("Доступний у будні", default=True)
    availability_weekends = models.BooleanField("Доступний у вихідні", default=False)
    availability_evenings = models.BooleanField("Доступний ввечері", default=False)

    # Бюджет/діапазон цін
    budget_min = models.PositiveIntegerField("Мінімальний бюджет (грн)", default=0)
    budget_max = models.PositiveIntegerField("Максимальний бюджет (грн)", default=0)

    # Мови
    language_uk = models.BooleanField("Українська", default=True)
    language_ru = models.BooleanField("Російська", default=False)
    language_en = models.BooleanField("Англійська", default=False)
    language_other = models.CharField("Інші мови", max_length=100, blank=True)

    # Інтереси/напрями
    interested_home = models.BooleanField("Домашні послуги (прибирання, ремонт)", default=False)
    interested_children = models.BooleanField("Діти/догляд/репетитори", default=False)
    interested_pets = models.BooleanField("Тварини", default=False)
    interested_auto = models.BooleanField("Авто", default=False)
    interested_it = models.BooleanField("IT/розробка/дизайн", default=False)
    interested_marketing = models.BooleanField("Маркетинг/копірайт", default=False)
    interested_translation = models.BooleanField("Переклад", default=False)
    interested_admin = models.BooleanField("Адміністрування/підтримка", default=False)

    # Додатково
    prefer_online = models.BooleanField("Переважно онлайн-послуги", default=True)
    prefer_verified = models.BooleanField("Хочу бачити лише перевірених виконавців", default=False)
    notes = models.TextField("Побажання/деталі", max_length=1000, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "детальна анкета"
        verbose_name_plural = "детальні анкети"

    def __str__(self):
        return f"Анкета {self.user.username}"
