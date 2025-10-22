from http import HTTPStatus

from core.tests.factories import CustomUserFactory
from django.test import TestCase


class CustomUserPublicProfileViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUserFactory(
            with_first_name=True,
            with_last_name=True,
            with_speciality=True,
            with_skills=True,
            with_description=True,
            with_country=True,
            with_city=True,
            with_phone=True,
        )

    def test_public_profile_view_available(self):
        """Публичный профиль пользователя доступен по ссылке, может быть просмотрен
        незалогиненным посетителем, содержит инфо о пользователе."""
        url = f"/users/{self.user.username}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, self.user.username)
        self.assertContains(response, self.user.last_name)
        self.assertContains(response, self.user.first_name)
        self.assertContains(response, self.user.description)
        self.assertContains(response, self.user.country)
        self.assertContains(response, self.user.city)
        for skill in self.user.skills:
            self.assertContains(response, skill)
