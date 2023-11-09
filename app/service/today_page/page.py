from ..word import WordPicker
from .hard_words import PickDay, get_hard_words
from .schema import TodayPage
from .text_generator import generate_today_text


def get_today_page(user_id: int) -> TodayPage | None:
    # if we still have words for learning, we take words from yesterday
    if WordPicker().get_word_for_learning(user_id) is not None:
        words = get_hard_words(user_id, pick_day=PickDay.YESTERDAY)
    else:
        words = get_hard_words(user_id, pick_day=PickDay.TODAY)

    if not words:
        return None

    foreign_words = [word.foreign for word in words]
    sentences = generate_today_text(foreign_words)
    if not sentences:
        return None

    page = TodayPage(
        words=words,
        sentences=sentences,
    )

    return page
