from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

STATUS_CHOICES = [
    ("todo", "To Do"),
    ("in_progress", "In Progress"),
    ("done", "Done"),
]

PRIORITY_CHOICES = [
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High"),
]

COURSE_DEPARTMENT_CHOICES = [
    ("general", "General"),
    ("computer_science", "Computer Science"),
    ("mathematics", "Mathematics"),
    ("engineering", "Engineering"),
    ("business", "Business"),
    ("economics", "Economics"),
    ("history", "History"),
    ("science", "Science"),
    ("humanities", "Humanities"),
    ("psychology", "Psychology"),
    ("political_science", "Political Science"),
    ("english", "English"),
    ("languages", "Languages"),
    ("arts_design", "Arts and Design"),
    ("music", "Music"),
    ("communications", "Communications"),
    ("education", "Education"),
    ("health_sciences", "Health Sciences"),
    ("philosophy", "Philosophy"),
    ("law", "Law"),
]


# Create your models here.
class Course(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course_code = models.CharField(max_length=20, blank=True)
    name = models.CharField(max_length=100)
    term = models.CharField(max_length=50, blank=True)
    instructor = models.CharField(max_length=100, blank=True)
    meeting_days = models.CharField(max_length=50, blank=True)
    meeting_time = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True)
    zoom_link = models.URLField(blank=True)
    office_hours = models.CharField(max_length=200, blank=True)
    syllabus_url = models.URLField(blank=True)
    syllabus_file = models.FileField(upload_to="syllabi/", blank=True, null=True)
    grading_notes = models.TextField(blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True)
    department = models.CharField(
        max_length=32,
        choices=COURSE_DEPARTMENT_CHOICES,
        blank=True,
        default="general",
    )

    def __str__(self):
        if self.course_code:
            return f"{self.course_code} {self.name}"
        return self.name

    def get_absolute_url(self):
        return reverse("course-detail", kwargs={"pk": self.id})


class Assignment(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="assignments"
    )
    resources = models.ManyToManyField(
        "StudyResource", blank=True, related_name="assignments"
    )
    title = models.CharField(max_length=150)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="todo")
    priority = models.CharField(
        max_length=20, choices=PRIORITY_CHOICES, default="medium"
    )
    notes = models.TextField(blank=True)

    def __str__(self):
        return self.title


class StudyResource(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    url = models.URLField(blank=True)  # optional
    resource_type = models.CharField(
        max_length=50, blank=True
    )  # video/article/slides/textbook
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("resource-detail", kwargs={"pk": self.id})
