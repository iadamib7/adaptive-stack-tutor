from __future__ import annotations

from backend.app.learning.adaptive_engine.models import (
    AdaptiveDecision,
    AdaptiveLearnerState,
    AdaptiveQuestion,
    ResponseEvidence,
)

from backend.app.learning.adaptive_engine.selector import (
    DeterministicAdaptiveSelector,
)


class CurriculumIndependentAdaptiveEngine:
    """
    Core adaptive engine.

    No curriculum, course, concept graph, or
    national standard is required.
    """

    def __init__(
        self,
        questions: list[AdaptiveQuestion],
        selector: (
            DeterministicAdaptiveSelector
            | None
        ) = None,
    ) -> None:
        self._questions = list(
            questions
        )

        self._selector = (
            selector
            or DeterministicAdaptiveSelector()
        )

        self._learners: dict[
            int,
            AdaptiveLearnerState,
        ] = {}

    def start(
        self,
        learner_id: int,
    ) -> AdaptiveDecision | None:
        learner = self.get_or_create_learner(
            learner_id
        )

        return self._selector.select(
            questions=self._questions,
            learner=learner,
        )

    def submit(
        self,
        *,
        learner_id: int,
        evidence: ResponseEvidence,
    ) -> AdaptiveDecision | None:
        learner = self.get_or_create_learner(
            learner_id
        )

        learner.record(
            evidence
        )

        return self._selector.select(
            questions=self._questions,
            learner=learner,
        )

    def get_or_create_learner(
        self,
        learner_id: int,
    ) -> AdaptiveLearnerState:
        if learner_id <= 0:
            raise ValueError(
                "learner_id must be positive."
            )

        learner = self._learners.get(
            learner_id
        )

        if learner is None:
            learner = AdaptiveLearnerState(
                learner_id=learner_id
            )

            self._learners[
                learner_id
            ] = learner

        return learner
