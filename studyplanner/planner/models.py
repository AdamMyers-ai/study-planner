from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Course(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    instructor = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name
