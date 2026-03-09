from django.db import migrations, models


COLOR_TO_DEPARTMENT = {
    "slate": "general",
    "blue": "computer_science",
    "green": "science",
    "amber": "history",
    "rose": "humanities",
    "teal": "mathematics",
}

DEPARTMENT_TO_COLOR = {value: key for key, value in COLOR_TO_DEPARTMENT.items()}


def map_color_to_department(apps, schema_editor):
    Course = apps.get_model("planner", "Course")

    for course in Course.objects.all().iterator():
        course.department = COLOR_TO_DEPARTMENT.get(course.department, "general")
        course.save(update_fields=["department"])


def map_department_to_color(apps, schema_editor):
    Course = apps.get_model("planner", "Course")

    for course in Course.objects.all().iterator():
        course.department = DEPARTMENT_TO_COLOR.get(course.department, "slate")
        course.save(update_fields=["department"])


class Migration(migrations.Migration):

    dependencies = [
        ("planner", "0005_course_course_code_course_end_date_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="course",
            old_name="color",
            new_name="department",
        ),
        migrations.RunPython(map_color_to_department, map_department_to_color),
        migrations.AlterField(
            model_name="course",
            name="department",
            field=models.CharField(
                blank=True,
                choices=[
                    ("general", "General"),
                    ("computer_science", "Computer Science"),
                    ("mathematics", "Mathematics"),
                    ("history", "History"),
                    ("science", "Science"),
                    ("humanities", "Humanities"),
                ],
                default="general",
                max_length=32,
            ),
        ),
    ]
