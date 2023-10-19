import random
from enum import Enum


class Difficulty(float, Enum):
    HARD = 1
    NORMAL = 1.7
    EASY = 2.5


def _add_randomness(value: float) -> float:
    MU = 1
    SIGMA = 0.07
    scale = random.gauss(MU, SIGMA)
    return value * scale


def apply_multiplier(period: float, difficulty: Difficulty) -> int:
    new_period = period * difficulty
    if difficulty != Difficulty.HARD:
        new_period = _add_randomness(new_period)

    MAX_PERIOD_MINUTE = 60 * 24 * 60  # 60 days
    new_period = min(new_period, MAX_PERIOD_MINUTE)

    return int(new_period)
