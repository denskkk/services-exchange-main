import factory
from exchange.models import Category
from users.models import CustomUser

from core.tests import faker


class CustomUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CustomUser

    username = factory.LazyAttribute(lambda _: faker.user_name())
    password = "password"
    email = factory.LazyAttribute(lambda _: faker.email())

    class Params:
        with_first_name = factory.Trait(first_name=faker.first_name())
        with_last_name = factory.Trait(last_name=faker.last_name())
        with_speciality = factory.Trait(speciality=faker.sentence()[:50])
        with_skills = factory.Trait(skills=faker.words(nb=10))
        with_description = factory.Trait(description=" ".join(faker.sentences(nb=5)))
        with_country = factory.Trait(country=faker.country())
        with_city = factory.Trait(city=faker.city())
        with_phone = factory.Trait(phone=faker.phone_number())

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Установим пользователю пароль, как положено."""
        user = super()._create(model_class, *args, **kwargs)
        user.set_password(cls.password)
        user.save()
        return user


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    title = factory.LazyAttribute(lambda _: faker.words(nb=5)[70:])
