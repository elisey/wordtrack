# Generated by Django 4.2.6 on 2023-11-06 22:12

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("app", "0003_alter_word_unique_together"),
    ]

    operations = [
        migrations.CreateModel(
            name="LearningHistory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "command",
                    models.CharField(
                        choices=[
                            ("LEARNING_HARD", "Learning Hard"),
                            ("LEARNING_NORMAL", "Learning Normal"),
                            ("LEARNING_KNOW", "Learning Know"),
                            ("LEARNING_AFTER_MONTH", "Learning After a Month"),
                            ("LEARNING_DELETE", "Learning Delete"),
                            ("REPEAT_RESET", "Repeat Reset"),
                            ("REPEAT_AGAIN", "Repeat Again"),
                            ("REPEAT_HARD", "Repeat Hard"),
                            ("REPEAT_NORMAL", "Repeat Normal"),
                            ("REPEAT_EASY", "Repeat Easy"),
                        ],
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ("word", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="app.word")),
            ],
        ),
    ]
