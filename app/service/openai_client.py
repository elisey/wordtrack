from abc import ABC, abstractmethod

import openai


class OpenAIClientBase(ABC):
    @abstractmethod
    def exchange(self, prompt: str) -> str | None:
        raise NotImplementedError


class OpenAIClient(OpenAIClientBase):
    def __init__(self, temperature: float = 0.4, model: str = "gpt-3.5-turbo") -> None:
        self.temperature = temperature
        self.model = model

    def exchange(self, prompt: str) -> str | None:
        context = [
            {"role": "user", "content": prompt},
        ]

        try:
            completion = openai.ChatCompletion.create(
                model=self.model,
                messages=context,
                temperature=self.temperature,
            )  # type:ignore[no-untyped-call]
            response: str = completion.choices[0].message.content
            return response
        except openai.OpenAIError:
            return None


def get_openai_client() -> OpenAIClientBase:
    return OpenAIClient()
