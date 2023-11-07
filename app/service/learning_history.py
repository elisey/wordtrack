import datetime

from django.db.models import Count

from ..models import LearningHistory  # type: ignore[attr-defined]
from .commands import Command


def add_history_event(user_id: int, word_id: int, command: Command) -> None:
    LearningHistory.objects.create(
        user_id=user_id,
        word_id=word_id,
        command=command.value,
    )


def get_todays_hard_words(user_id: int) -> list[str]:
    """
    Get words learned today.
    Sorted by number of attempts to learn it.
    """
    words_limit = 15
    today = datetime.date.today()
    filter_by_command = Command.LEARNING_HARD.value

    query_result = (
        LearningHistory.objects.filter(created_at__date=today, word__user_id=user_id, command=filter_by_command)
        .values_list("word__foreign", flat=True)
        .annotate(command_count=Count("id"))
        .order_by("-command_count")[:words_limit]
    )
    return list(query_result)
