import dataclasses
import enum

from app.service.learned_counter_repository import LearnCounter
from app.service.word import Status, Word


class Command(enum.Enum):
    LEARNING_HARD = "LEARNING_HARD"
    LEARNING_NORMAL = "LEARNING_NORMAL"
    LEARNING_KNOW = "LEARNING_KNOW"
    LEARNING_AFTER_MONTH = "LEARNING_AFTER_MONTH"
    LEARNING_DELETE = "LEARNING_DELETE"

    REPEAT_RESET = "REPEAT_RESET"
    REPEAT_AGAIN = "REPEAT_AGAIN"
    REPEAT_HARD = "REPEAT_HARD"
    REPEAT_NORMAL = "REPEAT_NORMAL"
    REPEAT_EASY = "REPEAT_EASY"


@dataclasses.dataclass
class CommandItem:
    text: str
    command: Command


class Commands:
    def create_commands(self, word: Word) -> tuple[CommandItem, ...]:
        if word.status in (Status.NEW, Status.LEARN):
            return self.create_commands_for_new()
        return self.create_commands_for_repeat()

    def create_commands_for_new(self) -> tuple[CommandItem, ...]:
        return (
            CommandItem(
                text="Не помню",
                command=Command.LEARNING_HARD,
            ),
            CommandItem(
                text="Помню",
                command=Command.LEARNING_NORMAL,
            ),
            CommandItem(
                text="Я его выучил",
                command=Command.LEARNING_KNOW,
            ),
            CommandItem(
                text="Я его знаю, напомнить через месяц",
                command=Command.LEARNING_AFTER_MONTH,
            ),
            CommandItem(
                text="Удалить",
                command=Command.LEARNING_DELETE,
            ),
        )

    def create_commands_for_repeat(self) -> tuple[CommandItem, ...]:
        return (
            CommandItem(
                text="Учить заново",
                command=Command.REPEAT_RESET,
            ),
            CommandItem(
                text="Повторить завтра",
                command=Command.REPEAT_AGAIN,
            ),
            CommandItem(
                text="Тяжело",
                command=Command.REPEAT_HARD,
            ),
            CommandItem(
                text="Нормально",
                command=Command.REPEAT_NORMAL,
            ),
            CommandItem(
                text="Супер легко",
                command=Command.REPEAT_EASY,
            ),
        )


def apply_command(command: Command, word: Word) -> None:
    if word.status == Status.NEW and command in (
        Command.LEARNING_HARD,
        Command.LEARNING_NORMAL,
    ):
        LearnCounter().increment_learned_counter()

    commands = {
        Command.LEARNING_HARD: word.set_learn_result_hard,
        Command.LEARNING_NORMAL: word.set_learn_result_normal,
        Command.LEARNING_KNOW: word.set_learn_result_learned,
        Command.LEARNING_AFTER_MONTH: word.set_learn_result_already_know,
        Command.LEARNING_DELETE: word.set_learn_result_drop,
        Command.REPEAT_RESET: word.set_repeat_result_learn_again,
        Command.REPEAT_AGAIN: word.set_repeat_result_repeat_tomorrow,
        Command.REPEAT_HARD: word.set_repeat_result_hard,
        Command.REPEAT_NORMAL: word.set_repeat_result_normal,
        Command.REPEAT_EASY: word.set_repeat_result_easy,
    }

    try:
        func = commands[command]
    except KeyError as ex:
        raise ValueError(f"Invalid command {command}") from ex
    func()
