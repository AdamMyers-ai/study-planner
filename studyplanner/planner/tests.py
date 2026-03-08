from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Assignment, Course


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


class CourseDetailViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="courseuser", password="StrongPass123!"
        )
        self.course = Course.objects.create(user=self.user, name="Science 101")
        Assignment.objects.create(
            course=self.course,
            title="Lab report",
            due_date=date.today(),
            status="done",
        )
        Assignment.objects.create(
            course=self.course,
            title="Quiz prep",
            due_date=date.today(),
            status="todo",
        )

    def test_course_detail_shows_completed_assignment_count(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("course-detail", args=[self.course.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Completed Assignments:")
        self.assertContains(response, "1 / 2")


class AssignmentCompleteViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="assignmentuser", password="StrongPass123!"
        )
        self.other_user = get_user_model().objects.create_user(
            username="otheruser", password="StrongPass123!"
        )
        self.course = Course.objects.create(user=self.user, name="Math 101")
        self.assignment = Assignment.objects.create(
            course=self.course,
            title="Finish worksheet",
            due_date=date.today(),
            status="todo",
        )

    def test_post_marks_assignment_complete(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("assignment-complete", args=[self.assignment.pk])
        )

        self.assignment.refresh_from_db()
        self.assertEqual(self.assignment.status, "done")
        self.assertRedirects(
            response, reverse("assignment-detail", args=[self.assignment.pk])
        )

    def test_post_marks_assignment_complete_and_redirects_to_course(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("assignment-complete", args=[self.assignment.pk]),
            {"redirect_to": "course"},
        )

        self.assignment.refresh_from_db()
        self.assertEqual(self.assignment.status, "done")
        self.assertRedirects(response, self.course.get_absolute_url())

    def test_post_marks_assignment_incomplete(self):
        self.assignment.status = "done"
        self.assignment.save(update_fields=["status"])
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("assignment-incomplete", args=[self.assignment.pk])
        )

        self.assignment.refresh_from_db()
        self.assertEqual(self.assignment.status, "todo")
        self.assertRedirects(
            response, reverse("assignment-detail", args=[self.assignment.pk])
        )

    def test_post_marks_assignment_incomplete_and_redirects_to_course(self):
        self.assignment.status = "done"
        self.assignment.save(update_fields=["status"])
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("assignment-incomplete", args=[self.assignment.pk]),
            {"redirect_to": "course"},
        )

        self.assignment.refresh_from_db()
        self.assertEqual(self.assignment.status, "todo")
        self.assertRedirects(response, self.course.get_absolute_url())

    def test_cannot_complete_another_users_assignment(self):
        other_course = Course.objects.create(user=self.other_user, name="History 201")
        other_assignment = Assignment.objects.create(
            course=other_course,
            title="Essay draft",
            due_date=date.today(),
            status="todo",
        )
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("assignment-complete", args=[other_assignment.pk])
        )

        self.assertEqual(response.status_code, 404)

    def test_cannot_mark_another_users_assignment_incomplete(self):
        other_course = Course.objects.create(user=self.other_user, name="History 201")
        other_assignment = Assignment.objects.create(
            course=other_course,
            title="Essay draft",
            due_date=date.today(),
            status="done",
        )
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("assignment-incomplete", args=[other_assignment.pk])
        )

        self.assertEqual(response.status_code, 404)
