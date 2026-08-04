from random import Random
from typing import Protocol

from backend.app.learning.sequencing.models import (
    NextQuestionOption,
)


class ChoiceStrategy(Protocol):
    def choose(
        self,
        candidates: list[NextQuestionOption],
    ) -> NextQuestionOption | None:
        ...


class FixedChoiceStrategy:
    def choose(
        self,
        candidates: list[NextQuestionOption],
    ) -> NextQuestionOption | None:
        if not candidates:
            return None

        return candidates[0]


class WeightedRandomChoiceStrategy:
    def __init__(
        self,
        random_generator: Random | None = None,
    ) -> None:
        self.random_generator = random_generator or Random()

    def choose(
        self,
        candidates: list[NextQuestionOption],
    ) -> NextQuestionOption | None:
        if not candidates:
            return None

        weights = [
            candidate.weight
            for candidate in candidates
        ]

        return self.random_generator.choices(
            candidates,
            weights=weights,
            k=1,
        )[0]
