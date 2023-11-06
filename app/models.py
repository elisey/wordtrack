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


class Commands(models.TextChoices):
    LEARNING_HARD = "LEARNING_HARD", _("Learning Hard")
    LEARNING_NORMAL = "LEARNING_NORMAL", _("Learning Normal")
    LEARNING_KNOW = "LEARNING_KNOW", _("Learning Know")
    LEARNING_AFTER_MONTH = "LEARNING_AFTER_MONTH", _("Learning After a Month")
    LEARNING_DELETE = "LEARNING_DELETE", _("Learning Delete")

    REPEAT_RESET = "REPEAT_RESET", _("Repeat Reset")
    REPEAT_AGAIN = "REPEAT_AGAIN", _("Repeat Again")
    REPEAT_HARD = "REPEAT_HARD", _("Repeat Hard")
    REPEAT_NORMAL = "REPEAT_NORMAL", _("Repeat Normal")
    REPEAT_EASY = "REPEAT_EASY", _("Repeat Easy")


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


class LearningHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    command = models.CharField(max_length=20, choices=Commands.choices)
    created_at = models.DateTimeField(auto_now_add=True)
