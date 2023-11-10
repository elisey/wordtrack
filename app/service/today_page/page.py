import datetime

from ..word import WordPicker
from .hard_words import get_hard_words
from .schema import TodayPage
from .storage import get_content as get_cached_content
from .storage import save_content as save_content_to_cache
from .text_generator import generate_today_text


def _get_page_title(pick_day: datetime.date) -> str:
    return "Difficult words for " + pick_day.strftime("%d %B %Y")


def _generate_page(user_id: int, pick_day: datetime.date) -> TodayPage | None:
    words = get_hard_words(user_id, pick_day)

    if not words:
        return None

    foreign_words = [word.foreign for word in words]
    sentences = generate_today_text(foreign_words)
    if not sentences:
        return None

    return TodayPage(
        title=_get_page_title(pick_day=pick_day),
        words=words,
        sentences=sentences,
    )


def get_today_page(user_id: int) -> TodayPage | None:
    # if we still have words for learning, we take words from yesterday
    if WordPicker().get_word_for_learning(user_id) is not None:
        pick_day = datetime.date.today() - datetime.timedelta(days=1)
    else:
        pick_day = datetime.date.today()

    page = get_cached_content(user_id, pick_day)
    if page is not None:
        return page

    page = _generate_page(user_id, pick_day)
    if page is None:
        return None

    save_content_to_cache(user_id, pick_day, page)
    return page
