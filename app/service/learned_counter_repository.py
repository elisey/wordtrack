import datetime

from django.db.models import F

from ..models import LearnedCount  # type: ignore[attr-defined]


class LearnCounter:
    def get_learned_counter(self) -> int:
        today = datetime.date.today()
        try:
            count = int(LearnedCount.objects.get(date=today).count)
        except LearnedCount.DoesNotExist:
            count = 0
            self.set_learned_counter(count)
        return count

    def set_learned_counter(self, value: int) -> None:
        today = datetime.date.today()
        LearnedCount.objects.update_or_create(date=today, count=value)

    def increment_learned_counter(self) -> None:
        today = datetime.date.today()

        updated = LearnedCount.objects.filter(date=today).update(count=F("count") + 1)
        if not updated:
            count = 1
            self.set_learned_counter(count)
