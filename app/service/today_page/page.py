from .hard_words import get_hard_words
from .schema import TodayPage
from .text_generator import generate_today_text


def get_today_page(user_id: int) -> TodayPage | None:
    words = get_hard_words(user_id)

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
