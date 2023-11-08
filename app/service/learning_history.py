from ..models import LearningHistory  # type: ignore[attr-defined]
from .commands import Command


def add_history_event(user_id: int, word_id: int, command: Command) -> None:
    LearningHistory.objects.create(
        user_id=user_id,
        word_id=word_id,
        command=command.value,
    )
