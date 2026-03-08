from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class AuthFlowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="StrongPass123!"
        )

    def test_login_redirects_to_course_list_by_default(self):
        response = self.client.post(
            reverse("login"),
            {"username": "testuser", "password": "StrongPass123!"},
        )

        self.assertRedirects(response, reverse("course-list"))

    def test_login_template_preserves_next_parameter(self):
        response = self.client.get(reverse("login"), {"next": reverse("course-list")})

        self.assertContains(
            response,
            f'type="hidden" name="next" value="{reverse("course-list")}"',
        )

    def test_login_redirects_to_next_when_present(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "testuser",
                "password": "StrongPass123!",
                "next": reverse("resource-list"),
            },
        )

        self.assertRedirects(response, reverse("resource-list"))

    def test_signup_redirects_to_course_list_by_default(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "newuser",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )

        self.assertRedirects(response, reverse("course-list"))
        self.assertTrue("_auth_user_id" in self.client.session)

    def test_signup_redirects_to_safe_next_when_present(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "nextuser",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
                "next": reverse("resource-list"),
            },
        )

        self.assertRedirects(response, reverse("resource-list"))

    def test_signup_ignores_unsafe_next_url(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "unsafeuser",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
                "next": "https://malicious.example/phish",
            },
        )

        self.assertRedirects(response, reverse("course-list"))

    def test_logout_redirects_to_home(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse("logout"))

        self.assertRedirects(response, reverse("home"))
