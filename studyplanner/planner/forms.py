from django import forms
from .models import Assignment, StudyResource


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ["title", "due_date", "status", "priority", "notes", "resources"]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields["resources"].queryset = StudyResource.objects.filter(user=user)
