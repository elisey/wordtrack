# type: ignore
import datetime

from django.contrib import admin

from .models import LearnedCount, Word


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = [
        "native",
        "foreign",
        "status",
        "group",
        "learning_stage",
        "period",
    ]
    search_fields = ["native", "foreign"]
    ordering = ["group"]
    list_filter = ("status",)

    def period(self, obj: Word) -> datetime.timedelta:
        return datetime.timedelta(minutes=obj.repetition_period)


@admin.register(LearnedCount)
class LearnedCountAdmin(admin.ModelAdmin):
    list_display = ["date", "count"]
