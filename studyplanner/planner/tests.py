from datetime import date

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
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
        self.course = Course.objects.create(
            user=self.user,
            course_code="SCI-101",
            name="Science 101",
            term="Spring 2026",
            instructor="Dr. Ada",
            meeting_days="Mon/Wed",
            meeting_time="10:00 AM - 11:15 AM",
            location="Building A, Room 201",
            zoom_link="https://example.com/zoom",
            office_hours="Tue 2 PM - 4 PM",
            syllabus_url="https://example.com/syllabus",
            grading_notes="Labs are 40% of the final grade.",
            start_date=date(2026, 1, 12),
            end_date=date(2026, 5, 1),
            notes="Bring calculator.",
            color="blue",
        )
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
        self.assertContains(response, "SCI-101 - Science 101")
        self.assertContains(response, "Spring 2026")
        self.assertContains(response, "Join Class")
        self.assertContains(response, "Open Syllabus")
        self.assertContains(response, "Bring calculator.")
        self.assertContains(response, "Completed Assignments")
        self.assertContains(response, "1 / 2")


class CourseCreateViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="createcourseuser", password="StrongPass123!"
        )

    def test_create_course_saves_extended_fields(self):
        self.client.force_login(self.user)
        syllabus_file = SimpleUploadedFile("syllabus.txt", b"syllabus content")

        response = self.client.post(
            reverse("course-create"),
            {
                "course_code": "MATH-220",
                "name": "Linear Algebra",
                "term": "Fall 2026",
                "instructor": "Prof. Noether",
                "meeting_days": "Tue/Thu",
                "meeting_time": "1:00 PM - 2:15 PM",
                "location": "Science Hall 12",
                "zoom_link": "https://example.com/linear-algebra",
                "office_hours": "Wed 3 PM - 5 PM",
                "syllabus_url": "https://example.com/linear-syllabus",
                "syllabus_file": syllabus_file,
                "grading_notes": "Exams are worth 60%.",
                "start_date": "2026-08-24",
                "end_date": "2026-12-10",
                "notes": "Review matrix multiplication weekly.",
                "color": "teal",
            },
        )

        course = Course.objects.get(name="Linear Algebra")
        self.assertRedirects(response, course.get_absolute_url())
        self.assertEqual(course.user, self.user)
        self.assertEqual(course.course_code, "MATH-220")
        self.assertEqual(course.term, "Fall 2026")
        self.assertEqual(course.meeting_days, "Tue/Thu")
        self.assertEqual(course.color, "teal")
        self.assertTrue(bool(course.syllabus_file))


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
