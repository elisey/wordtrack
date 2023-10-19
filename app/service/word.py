import dataclasses
import datetime
import enum
import random
import typing

from django.db.models import QuerySet

from app.service.difficulty_multipliers import Difficulty, apply_multiplier

from ..models import Status as StatusModel  # type: ignore[attr-defined]
from ..models import Word as WordModel  # type: ignore[attr-defined]
from .learned_counter_repository import LearnCounter


class Status(enum.StrEnum):
    NEW = "NEW"
    LEARN = "LEARN"
    REPEAT = "REPEAT"
    DELETE = "DELETE"


class ExerciseDirection(enum.StrEnum):
    TO_NATIVE = "TO_NATIVE"
    TO_FOREIGN = "TO_FOREIGN"


@dataclasses.dataclass
class Word:
    id: int | None
    native: str
    foreign: str
    status: Status
    last_repeated: datetime.date
    repeat_on: datetime.date
    learning_stage: int
    repetition_period: int
    next_repetition_direction: ExerciseDirection
    user_id: int
    group: str

    def __to_repeat_state(self, period_minutes: int) -> None:
        self.status = Status.REPEAT
        self.last_repeated = datetime.date.today()
        self.repetition_period = period_minutes
        self.repeat_on = datetime.date.today() + datetime.timedelta(minutes=period_minutes)
        self.next_repetition_direction = ExerciseDirection.TO_FOREIGN

    def __to_learning_state(self) -> None:
        self.status = Status.LEARN
        self.learning_stage = 0

    def __update_repetition_period(self, new_period_minutes: int) -> None:
        self.last_repeated = datetime.date.today()
        self.repetition_period = new_period_minutes
        self.repeat_on = datetime.date.today() + datetime.timedelta(minutes=new_period_minutes)

    def __reset_repetition_direction(self) -> None:
        self.next_repetition_direction = ExerciseDirection.TO_FOREIGN

    def __invert_repetition_direction(self) -> None:
        if self.next_repetition_direction == ExerciseDirection.TO_FOREIGN:
            self.next_repetition_direction = ExerciseDirection.TO_NATIVE
        else:
            self.next_repetition_direction = ExerciseDirection.TO_FOREIGN

    def set_learn_result_normal(self) -> None:
        self.status = Status.LEARN
        if self.learning_stage >= 3:
            self.__to_repeat_state(24 * 60)
        else:
            self.learning_stage += 1

    def set_learn_result_hard(self) -> None:
        self.status = Status.LEARN
        self.learning_stage = 0

    def set_learn_result_learned(self) -> None:
        self.__to_repeat_state(24 * 60)

    def set_learn_result_already_know(self) -> None:
        self.__to_repeat_state(30 * 24 * 60)

    def set_learn_result_drop(self) -> None:
        self.status = Status.DELETE

    def set_repeat_result_learn_again(self) -> None:
        self.__to_learning_state()

    def set_repeat_result_repeat_tomorrow(self) -> None:
        self.__update_repetition_period(24 * 60)
        self.__reset_repetition_direction()

    def set_repeat_result_hard(self) -> None:
        new_period = apply_multiplier(self.repetition_period, Difficulty.HARD)
        self.__update_repetition_period(new_period)
        self.__invert_repetition_direction()

    def set_repeat_result_normal(self) -> None:
        new_period = apply_multiplier(self.repetition_period, Difficulty.NORMAL)
        self.__update_repetition_period(new_period)
        self.__invert_repetition_direction()

    def set_repeat_result_easy(self) -> None:
        new_period = apply_multiplier(self.repetition_period, Difficulty.EASY)
        self.__update_repetition_period(new_period)
        self.__invert_repetition_direction()

    def save(self) -> None:
        if self.id:
            WordModel.objects.filter(pk=self.id).update(
                user_id=self.user_id,
                native=self.native,
                foreign=self.foreign,
                status=self.status,
                last_repeated=self.last_repeated,
                repeat_on=self.repeat_on,
                learning_stage=self.learning_stage,
                repetition_period=self.repetition_period,
                next_repetition_direction=self.next_repetition_direction,
                group=self.group,
            )
        else:
            WordModel.objects.create(
                user_id=self.user_id,
                native=self.native,
                foreign=self.foreign,
                status=self.status,
                last_repeated=self.last_repeated,
                repeat_on=self.repeat_on,
                learning_stage=self.learning_stage,
                repetition_period=self.repetition_period,
                next_repetition_direction=self.next_repetition_direction,
                group=self.group,
            )

    @classmethod
    def from_model(cls, model: WordModel) -> typing.Self:
        return cls(
            id=model.pk,
            user_id=model.user_id,
            native=model.native,
            foreign=model.foreign,
            status=Status(model.status),
            last_repeated=model.last_repeated,
            repeat_on=model.repeat_on,
            learning_stage=model.learning_stage,
            repetition_period=model.repetition_period,
            next_repetition_direction=ExerciseDirection(model.next_repetition_direction),
            group=model.group,
        )


class WordPicker:
    def __init__(self) -> None:
        self.prev_word_id = -1

    def __get_random_from_qs(self, qs: QuerySet[WordModel]) -> Word | None:
        total_words = qs.count()
        if total_words == 0:
            return None
        random_index = random.randint(0, total_words - 1)
        random_word = qs[random_index]
        return Word.from_model(random_word)

    def __get_learning_word(self, user_id: int) -> Word | None:
        qs = WordModel.objects.filter(status=StatusModel.LEARN, user_id=user_id)
        return self.__get_random_from_qs(qs)

    def __get_new_word(self, user_id: int) -> Word | None:
        qs = WordModel.objects.filter(status=StatusModel.NEW, user_id=user_id)
        return self.__get_random_from_qs(qs)

    def __get_repeat_word(self, user_id: int) -> Word | None:
        today = datetime.date.today()
        qs = WordModel.objects.filter(repeat_on__lte=today, status=StatusModel.REPEAT, user_id=user_id)
        return self.__get_random_from_qs(qs)

    def get_word_for_learning(self, user_id: int) -> Word | None:
        word_to_repeat = self.__get_repeat_word(user_id)
        if LearnCounter().get_learned_counter() >= 5:
            word_to_learn = self.__get_learning_word(user_id)
        else:
            word_to_learn = self.__get_new_word(user_id)
            if not word_to_learn:
                word_to_learn = self.__get_learning_word(user_id)

        if word_to_learn and word_to_repeat:
            if random.randrange(0, 10) <= 7:
                return word_to_repeat
            return word_to_learn

        return word_to_learn or word_to_repeat or None

    def get_by_id(self, word_id: int, user_id: int) -> Word | None:
        model = WordModel.objects.filter(pk=word_id, user_id=user_id).first()
        if model is None:
            return None
        return Word.from_model(model)

    def create_new(self, user_id: int, native: str, foreign: str, group: str) -> Word:
        today = datetime.date.today()
        return Word(
            id=None,
            user_id=user_id,
            native=native,
            foreign=foreign,
            status=Status.NEW,
            last_repeated=today,
            repeat_on=today,
            learning_stage=0,
            repetition_period=0,
            next_repetition_direction=ExerciseDirection.TO_FOREIGN,
            group=group,
        )
