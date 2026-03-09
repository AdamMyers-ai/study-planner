from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("planner", "0006_rename_color_to_department"),
    ]

    operations = [
        migrations.AlterField(
            model_name="course",
            name="department",
            field=models.CharField(
                blank=True,
                choices=[
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
                ],
                default="general",
                max_length=32,
            ),
        ),
    ]
