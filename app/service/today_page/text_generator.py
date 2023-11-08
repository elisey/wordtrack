import json

import openai
from django.conf import settings
from jsonschema.exceptions import ValidationError
from jsonschema.validators import validate

from app.service.today_page.schema import Sentence


# todo move to another file
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


def generate_today_text(words: list[str]) -> list[Sentence] | None:
    openai.api_key = settings.OPENAI_API_KEY
    words_str = ", ".join(words)
    prompt = f"""Step 1. Make the text in Dutch. Sentences must be connected in meaning. The text must have a story. Preferable use present tense. Provide 10 sentences. Use this words in it separated with ,
{words_str}

Step 2. Translate each sentence to English.

Step 3. Provide result as a json. It should be list of objects. key "foreign" - sentence in dutch. Key "native" - sentence in english.

Example:
[
    {{
        "foreign": "Voorzichtig liep de postbode door het park, genietend van de prachtige lenteochtend.",
        "native": "Carefully, the mailman walked through the park, enjoying the beautiful spring morning."
    }},
    {{
        "foreign": "Gauw stapte hij op zijn fiets en begon aan zijn dagelijkse ronde.",
        "native": "Quickly, he hopped on his bike and started his daily round."
    }},
    {{
        "foreign": "Onderweg bezorgde hij vrolijk de brieven en pakketjes bij de huizen.",
        "native": "Along the way, he cheerfully delivered the letters and packages to the houses."
    }}
]"""

    context = [
        {"role": "user", "content": prompt},
    ]

    response = _open_api_exchange(context)
    if response is None:
        return None

    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {"foreign": {"type": "string"}, "native": {"type": "string"}},
            "required": ["foreign", "native"],
        },
    }

    try:
        data_dict = json.loads(response)
    except json.JSONDecodeError:
        # todo add logging
        return None

    try:
        validate(data_dict, schema)
    except ValidationError:
        return None

    result = []
    for item in data_dict:
        sentence = Sentence(foreign=item["foreign"], native=item["native"])
        result.append(sentence)
    return result
