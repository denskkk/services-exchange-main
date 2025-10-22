from http import HTTPStatus

from core.tests.factories import CategoryFactory
from django.test import TestCase


class CustomUserPublicProfileViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.categories = []
        for i in range(100):
            category = CategoryFactory()
            cls.categories.append(category)

    def test_category_list_view(self):
        """Проверяем, что страница со списком рубрик по нужному адресу, и все категории
        выводятся на странице."""
        url = "/exchange/categories/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        for category in self.categories:
            self.assertContains(response, category.title)
