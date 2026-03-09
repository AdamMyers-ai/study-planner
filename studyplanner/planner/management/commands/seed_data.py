from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from planner.models import Course, Assignment, StudyResource


class Command(BaseCommand):
    help = "Seed demo data"

    def handle(self, *args, **kwargs):
        user, created = User.objects.get_or_create(username="demo_user")
        if created:
            user.set_password("password123")
            user.save()

        course1, _ = Course.objects.get_or_create(
            user=user,
            name="Computer Science 101",
            defaults={"instructor": "Dr. Smith", "color": "blue"},
        )

        course2, _ = Course.objects.get_or_create(
            user=user,
            name="History 201",
            defaults={"instructor": "Prof. Johnson", "color": "green"},
        )

        resource1, _ = StudyResource.objects.get_or_create(
            user=user,
            title="Lecture Slides",
            defaults={
                "url": "https://example.com/slides",
                "resource_type": "slides",
                "description": "Week 1 lecture slides",
            },
        )

        resource2, _ = StudyResource.objects.get_or_create(
            user=user,
            title="YouTube Review Video",
            defaults={
                "url": "https://example.com/video",
                "resource_type": "video",
                "description": "Helpful overview video",
            },
        )

        assignment1, _ = Assignment.objects.get_or_create(
            course=course1,
            title="Python Homework",
            defaults={
                "due_date": date.today() + timedelta(days=1),
                "status": "todo",
                "priority": "high",
                "notes": "Complete chapter exercises",
            },
        )

        assignment2, _ = Assignment.objects.get_or_create(
            course=course2,
            title="Essay Outline",
            defaults={
                "due_date": date.today() + timedelta(days=5),
                "status": "in_progress",
                "priority": "medium",
                "notes": "Draft thesis and outline",
            },
        )

        assignment1.resources.add(resource1, resource2)
        assignment2.resources.add(resource2)

        self.stdout.write(self.style.SUCCESS("Seed data created successfully."))
