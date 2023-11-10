import json

from jsonschema.exceptions import ValidationError
from jsonschema.validators import validate

from app.service.openai_client import get_openai_client
from app.service.today_page.schema import Sentence


def generate_today_text(words: list[str]) -> list[Sentence] | None:
    words_str = ", ".join(words)
    prompt = f"""Step 1. Make the text in Dutch. Sentences must be connected in meaning. The text must have a story. Preferable use present tense. Provide 15 sentences. Use this words in it separated with ,
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

    response = get_openai_client().exchange(prompt)
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
