import re

import openai
from django.conf import settings


def _open_api_exchange(context: list[dict[str, str]]) -> str | None:
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=context,
            temperature=0.4,
        )  # type:ignore[no-untyped-call]
        response: str = completion.choices[0].message.content
        return response
    except openai.OpenAIError:
        return None


def get_example(word: str) -> str | None:
    openai.api_key = settings.OPENAI_API_KEY

    prompt = f"""Дано слово на нидерландском - {word}. Твоя задача
1. Составлять простое предложение на нидерландском языке используя это слово.
2. Переводить предложение на английский язык
3. Выводить результат в следующем формате - предложение на нидерландском / предложение на английском
4. Всего составь 3 предложения. Каждый результат на отдельной строке. Предожения дожны иметь разнообразную структуру и набор слов.
Пример

Het huis heeft een rode voordeur en witte muren. / The house has a red front door and white walls.
In het huis zijn er grote ramen die veel licht binnenlaten. / In the house, there are large windows that let in a lot of light.
Mijn ouders wonen al jarenlang in het huis. / My parents have been living in the house for many years."""

    context = [
        {"role": "user", "content": prompt},
    ]

    result = _open_api_exchange(context)
    if result is None:
        return None
    result = result.replace("\n", "<br>\n")

    # making word bold in the sentences
    escape = re.escape(word)
    result = re.sub(rf"\b{escape}\b", lambda x: f"<b>{x.group(0)}</b>", result, flags=re.IGNORECASE)

    return result
