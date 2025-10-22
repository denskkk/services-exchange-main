from http import HTTPStatus

from django.test import TestCase


class IndexViewTest(TestCase):
    def test_index_view(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Биржа Услуг")
        self.assertContains(response, "Регистрация")
        self.assertContains(response, "Вход")
