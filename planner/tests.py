from datetime import date
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .models import Assignment, Course, StudyResource


class AuthFlowTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", password="StrongPass123!"
        )

    def test_login_redirects_to_dashboard_by_default(self):
        response = self.client.post(
            reverse("login"),
            {"username": "testuser", "password": "StrongPass123!"},
        )

        self.assertRedirects(response, reverse("home"))

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

    def test_signup_redirects_to_dashboard_by_default(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "newuser",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )

        self.assertRedirects(response, reverse("home"))
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

        self.assertRedirects(response, reverse("home"))

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
            department="science",
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
                "department": "mathematics",
            },
        )

        course = Course.objects.get(name="Linear Algebra")
        self.assertRedirects(response, course.get_absolute_url())
        self.assertEqual(course.user, self.user)
        self.assertEqual(course.course_code, "MATH-220")
        self.assertEqual(course.term, "Fall 2026")
        self.assertEqual(course.meeting_days, "Tue/Thu")
        self.assertEqual(course.department, "mathematics")
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


class AssignmentListViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="listuser", password="StrongPass123!"
        )
        other_user = get_user_model().objects.create_user(
            username="outsider", password="StrongPass123!"
        )
        self.course = Course.objects.create(user=self.user, name="Biology 101")
        other_course = Course.objects.create(user=other_user, name="Physics 101")
        Assignment.objects.create(
            course=self.course,
            title="Cell structure review",
            due_date=date.today(),
            status="todo",
            priority="high",
        )
        Assignment.objects.create(
            course=self.course,
            title="Lab notebook update",
            due_date=date.today(),
            status="done",
            priority="low",
        )
        Assignment.objects.create(
            course=other_course,
            title="Cell transport essay",
            due_date=date.today(),
            status="todo",
            priority="medium",
        )

    def test_assignment_list_filters_by_search_query(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("assignment-list"), {"q": "cell"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cell structure review")
        self.assertNotContains(response, "Lab notebook update")
        self.assertNotContains(response, "Cell transport essay")
        self.assertContains(response, 'value="cell"')


class StudyResourceViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="resourceuser", password="StrongPass123!"
        )
        self.course = Course.objects.create(user=self.user, name="Chemistry 101")
        self.assignment = Assignment.objects.create(
            course=self.course,
            title="Reaction worksheet",
            due_date=date.today(),
        )

    def test_create_resource_saves_choice_and_detail_shows_display_label(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("resource-create"),
            {
                "title": "Exam Practice Set",
                "url": "https://example.com/practice",
                "resource_type": "practice_problems",
                "description": "Timed practice questions.",
            },
        )

        resource = StudyResource.objects.get(title="Exam Practice Set")
        self.assertRedirects(response, resource.get_absolute_url())
        self.assertEqual(resource.resource_type, "practice_problems")

        detail_response = self.client.get(resource.get_absolute_url())

        self.assertContains(detail_response, "Practice Problems")

    def test_create_resource_for_assignment_attaches_and_redirects_to_assignment(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("assignment-resource-create", args=[self.assignment.pk]),
            {
                "title": "Stoichiometry Video",
                "url": "https://example.com/stoichiometry",
                "resource_type": "video",
                "description": "Walkthrough of the worksheet topics.",
            },
        )

        resource = StudyResource.objects.get(title="Stoichiometry Video")
        self.assignment.refresh_from_db()

        self.assertRedirects(
            response, reverse("assignment-detail", args=[self.assignment.pk])
        )
        self.assertIn(resource, self.assignment.resources.all())

    def test_assignment_create_view_links_to_resource_create_with_return_url(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("assignment-create", args=[self.course.pk]))

        expected_next = reverse("assignment-create", args=[self.course.pk])
        self.assertContains(
            response,
            f'{reverse("resource-create")}?next={expected_next}',
        )

    def test_create_resource_with_next_redirects_back_to_assignment_create(self):
        self.client.force_login(self.user)
        next_url = reverse("assignment-create", args=[self.course.pk])

        response = self.client.post(
            reverse("resource-create"),
            {
                "title": "Balancing Equations Notes",
                "url": "https://example.com/notes",
                "resource_type": "article",
                "description": "Reference notes for the assignment.",
                "next": next_url,
            },
        )

        resource = StudyResource.objects.get(title="Balancing Equations Notes")

        self.assertRedirects(response, next_url)
        self.assertEqual(resource.user, self.user)
