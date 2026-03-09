from django import forms
from .models import Assignment, Course, StudyResource


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ["title", "due_date", "status", "priority", "notes", "resources"]

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields["resources"].queryset = StudyResource.objects.filter(user=user)


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            "course_code",
            "name",
            "term",
            "instructor",
            "meeting_days",
            "meeting_time",
            "location",
            "zoom_link",
            "office_hours",
            "syllabus_url",
            "syllabus_file",
            "grading_notes",
            "start_date",
            "end_date",
            "notes",
            "color",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "grading_notes": forms.Textarea(attrs={"rows": 4}),
            "notes": forms.Textarea(attrs={"rows": 4}),
        }
