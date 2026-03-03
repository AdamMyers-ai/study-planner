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


# Create your models here.
class Course(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    instructor = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("course-detail", kwargs={"pk": self.id})


class Assignments(models.Model):
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="assignments"
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
