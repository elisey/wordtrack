import datetime
import json
from abc import ABC, abstractmethod
from dataclasses import asdict

from dacite import from_dict

from app.models import TodayPage as TodayPageModel  # type: ignore[attr-defined]

from .schema import TodayPage


class StorageInterface(ABC):
    @abstractmethod
    def get_content(self, date: datetime.date) -> TodayPage | None:
        raise NotImplementedError

    @abstractmethod
    def save_content(self, date: datetime.date, content: TodayPage) -> None:
        raise NotImplementedError


class Storage(StorageInterface):
    def __init__(self, user_id: int) -> None:
        self.user_id = user_id

    def get_content(self, date: datetime.date) -> TodayPage | None:
        try:
            content_str = TodayPageModel.objects.get(user_id=self.user_id, date=date).content
        except TodayPageModel.DoesNotExist:
            return None
        content = from_dict(data_class=TodayPage, data=json.loads(content_str))
        return content

    def save_content(self, date: datetime.date, content: TodayPage) -> None:
        content_str = json.dumps(asdict(content))
        TodayPageModel.objects.update_or_create(
            user_id=self.user_id,
            date=date,
            defaults={"content": content_str},
        )


def get_storage(user_id: int) -> StorageInterface:
    """Factory for Storage class."""
    return Storage(user_id)
