import datetime
import enum

from django.db.models import Count

from app.models import LearningHistory  # type: ignore[attr-defined]
from app.service.today_page.schema import Word


class PickDay(enum.Enum):
    TODAY = enum.auto()
    YESTERDAY = enum.auto()


def _filter_words(day: datetime.date, user_id: int, commands: list[str], limit: int) -> list[Word]:
    query_result = (
        LearningHistory.objects.filter(created_at__date=day, word__user_id=user_id, command__in=commands)
        .values("word__native", "word__foreign")
        .annotate(command_count=Count("id"))
        .order_by("-command_count")[:limit]
    )
    return [Word(native=item["word__native"], foreign=item["word__foreign"]) for item in query_result]


def get_hard_words(user_id: int, day: datetime.date) -> list[Word]:
    """
    Get words learned today.
    Sorted by number of attempts to learn it.
    """
    words_limit = 15

    filter_by_commands = ["LEARNING_HARD", "REPEAT_RESET"]

    words = _filter_words(day, user_id, filter_by_commands, words_limit)
    if len(words) < words_limit:
        words += _filter_words(day, user_id, ["REPEAT_AGAIN"], words_limit - len(words))
    return words
