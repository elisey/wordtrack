import dataclasses


@dataclasses.dataclass
class Word:
    native: str
    foreign: str


@dataclasses.dataclass
class Sentence:
    foreign: str
    native: str


@dataclasses.dataclass
class TodayPage:
    words: list[Word]
    sentences: list[Sentence]
