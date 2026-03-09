from django.db import migrations, models


NORMALIZED_RESOURCE_TYPES = {
    "video": "video",
    "videos": "video",
    "article": "article",
    "articles": "article",
    "slides": "slides",
    "slide_deck": "slides",
    "slide deck": "slides",
    "textbook": "textbook",
    "book": "textbook",
    "practice_problems": "practice_problems",
    "practice problems": "practice_problems",
    "practice-problems": "practice_problems",
    "problem set": "practice_problems",
    "problem_set": "practice_problems",
    "other": "other",
}


def normalize_resource_types(apps, schema_editor):
    StudyResource = apps.get_model("planner", "StudyResource")

    for resource in StudyResource.objects.all().iterator():
        raw_value = (resource.resource_type or "").strip().lower()
        if not raw_value:
            normalized = ""
        else:
            normalized = NORMALIZED_RESOURCE_TYPES.get(raw_value, "other")
        resource.resource_type = normalized
        resource.save(update_fields=["resource_type"])


class Migration(migrations.Migration):

    dependencies = [
        ("planner", "0007_expand_course_departments"),
    ]

    operations = [
        migrations.RunPython(normalize_resource_types, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="studyresource",
            name="resource_type",
            field=models.CharField(
                blank=True,
                choices=[
                    ("video", "Video"),
                    ("article", "Article"),
                    ("slides", "Slides"),
                    ("textbook", "Textbook"),
                    ("practice_problems", "Practice Problems"),
                    ("other", "Other"),
                ],
                max_length=50,
            ),
        ),
    ]
