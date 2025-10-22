from http import HTTPStatus

from core.tests.factories import CustomUserFactory
from django.test import TestCase
from django.urls import reverse

from users.models import CustomUser


class CustomUserUpdateViewTest(TestCase):
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

    def given_user_logged_in(self):
        url = reverse("account_login")
        self.client.post(
            url,
            {"login": self.user.email, "password": CustomUserFactory.password},
            follow=True,
        )

    def test_profile_update_view_302_for_anonymous(self):
        url = reverse("users:update", kwargs={"pk": self.user.pk})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

    def test_update_view_opens_with_login(self):
        self.given_user_logged_in()

        url = reverse("users:update", kwargs={"pk": self.user.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_update_view_works_with_correct_data(self):
        self.given_user_logged_in()

        new_username = "newUsername"
        new_first_name = "New First Name"
        new_last_name = "New Last Name"
        new_speciality = "New Speciality"
        new_description = "New Description"
        new_country = "New Country"
        new_city = "New City"
        new_phone = "+7(000)000-00-00"

        url = reverse("users:update", kwargs={"pk": self.user.pk})
        response = self.client.post(
            url,
            data={
                "username": new_username,
                "first_name": new_first_name,
                "last_name": new_last_name,
                "speciality": new_speciality,
                "description": new_description,
                "country": new_country,
                "city": new_city,
                "phone": new_phone,
            },
            follow=True,
        )

        updated_user = CustomUser.objects.get(pk=self.user.pk)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(updated_user.username, new_username)
        self.assertEqual(updated_user.first_name, new_first_name)
        self.assertEqual(updated_user.last_name, new_last_name)
        self.assertEqual(updated_user.speciality, new_speciality)
        self.assertEqual(updated_user.description, new_description)
        self.assertEqual(updated_user.country, new_country)
        self.assertEqual(updated_user.city, new_city)
        self.assertEqual(updated_user.phone, new_phone)
