# Generated by Django 4.2.5 on 2023-10-18 20:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="word",
            name="group",
            field=models.TextField(blank=True),
        ),
    ]
