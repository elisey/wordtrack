# type: ignore

from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models import TextField
from django.utils.translation import gettext_lazy as _


class Status(models.TextChoices):
    NEW = "NEW", _("New")
    LEARN = "LEARN", _("Learning")
    REPEAT = "REPEAT", _("Repeat")
    DELETE = "DELETE", _("Delete")


class ExerciseDirection(models.TextChoices):
    TO_NATIVE = "TO_NATIVE", _("To Native")
    TO_FOREIGN = "TO_FOREIGN", _("To Foreign")  # normal


class Word(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    native = TextField()
    foreign = TextField()
    status = models.CharField(
        max_length=6,
        choices=Status.choices,
        default=Status.NEW,
    )

    group = models.TextField(blank=True)

    # learning
    learning_stage = models.IntegerField(default=0)

    # repeat
    repeat_on = models.DateField(default=datetime.now)
    last_repeated = models.DateField(default=datetime.now)
    repetition_period = models.IntegerField(default=0)
    next_repetition_direction = models.CharField(
        max_length=14,
        choices=ExerciseDirection.choices,
        default=ExerciseDirection.TO_FOREIGN,
    )

    class Meta:
        unique_together = ["user", "native", "foreign"]


class LearnedCount(models.Model):
    date = models.DateField(unique=True)
    count = models.IntegerField()
