from __future__ import annotations

from dataclasses import replace

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
    Curriculum-independent adaptive engine.

    No curriculum, course, concept graph, or
    national standard is required.

    The engine selects a next question from the
    instructor's uploaded question bank after every
    learner response.

    Deterministic does not mean linear. Different
    learner states can produce different paths
    through the same question bank, while identical
    states produce identical decisions.

    Targeted support is one possible adaptive path.
    It does not force the learner into a mandatory
    remediation -> reassessment cycle.
    """

    def __init__(
        self,
        questions: list[AdaptiveQuestion],
        selector: (
            DeterministicAdaptiveSelector
            | None
        ) = None,
    ) -> None:
        self._questions = list(questions)

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

        decision = self._selector.select(
            questions=self._questions,
            learner=learner,
        )

        if decision is None:
            return None

        return replace(
            decision,
            decision_type="start",
            return_target_question_id=None,
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

        answered_question = (
            self._require_question(
                evidence.question_id
            )
        )

        learner.record(
            evidence,
            question=answered_question,
        )

        # A successful response to a question that
        # supports previously observed response
        # evidence reduces those outstanding needs.
        if evidence.score >= 1.0:
            self._resolve_supported_needs(
                learner=learner,
                question=answered_question,
            )

        decision = self._selector.select(
            questions=self._questions,
            learner=learner,
        )

        if decision is None:
            return None

        # Targeted support remains a possible branch,
        # but it does not create a mandatory return
        # to the question that preceded it.
        if (
            evidence.score < 1.0
            and decision.score.diagnostic_match
            > 0.0
        ):
            return replace(
                decision,
                decision_type="support",
                return_target_question_id=None,
                reason=(
                    "Response evidence increased the "
                    "priority of this support-relevant "
                    "question. "
                    + decision.reason
                ),
            )

        return replace(
            decision,
            decision_type="advance",
            return_target_question_id=None,
        )

    @staticmethod
    def _resolve_supported_needs(
        *,
        learner: AdaptiveLearnerState,
        question: AdaptiveQuestion,
    ) -> None:
        """
        Remove outstanding diagnostic needs that a
        successfully completed question explicitly
        supports.

        This prevents an old diagnostic signal from
        permanently dominating later selection.
        """

        supported = set(question.supports)

        if not supported:
            return

        for need in tuple(
            learner.misconception_counts
        ):
            if need not in supported:
                continue

            learner.misconception_counts.pop(
                need,
                None,
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

    def _require_question(
        self,
        question_id: str,
    ) -> AdaptiveQuestion:
        for question in self._questions:
            if (
                question.question_id
                == question_id
            ):
                return question

        raise ValueError(
            "Unknown adaptive question: "
            f"{question_id}"
        )