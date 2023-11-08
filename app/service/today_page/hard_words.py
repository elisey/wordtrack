import datetime

from django.db.models import Count

from app.models import LearningHistory  # type: ignore[attr-defined]
from app.service.today_page.schema import Word


def get_hard_words(user_id: int) -> list[Word]:
    """
    Get words learned today.
    Sorted by number of attempts to learn it.
    """
    words_limit = 15
    today = datetime.date.today() - datetime.timedelta(days=1)
    filter_by_command = "LEARNING_HARD"  # todo добавить еще статусы

    query_result = (
        LearningHistory.objects.filter(created_at__date=today, word__user_id=user_id, command=filter_by_command)
        .values("word__native", "word__foreign")
        .annotate(command_count=Count("id"))
        .order_by("-command_count")[:words_limit]
    )
    return [Word(native=item["word__native"], foreign=item["word__foreign"]) for item in query_result]
