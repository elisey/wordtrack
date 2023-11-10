import datetime
import json
from dataclasses import asdict

from dacite import from_dict

from app.models import TodayPage as TodayPageModel  # type: ignore[attr-defined]

from .schema import TodayPage


def get_content(user_id: int, date: datetime.date) -> TodayPage | None:
    try:
        content_str = TodayPageModel.objects.get(user_id=user_id, date=date).content
    except TodayPageModel.DoesNotExist:
        return None
    content = from_dict(data_class=TodayPage, data=json.loads(content_str))
    return content


def save_content(user_id: int, date: datetime.date, content: TodayPage) -> None:
    content_str = json.dumps(asdict(content))
    TodayPageModel.objects.update_or_create(
        user_id=user_id,
        date=date,
        defaults={"content": content_str},
    )
