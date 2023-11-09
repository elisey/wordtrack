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
    title: str
    words: list[Word]
    sentences: list[Sentence]
