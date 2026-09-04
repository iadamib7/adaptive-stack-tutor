from __future__ import annotations

from dataclasses import replace

from backend.app.learning.adaptive_engine.models import (
    AdaptiveDecision,
    AdaptiveLearnerState,
    AdaptiveQuestion,
    CandidateScore,
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

    The engine supports four routing actions:

        start
        advance
        remediate
        reassess

    Remediation is triggered when an incorrect
    response produces diagnostic evidence and the
    selector finds a question with a positive
    diagnostic match.

    A successful remediation returns the learner
    to the original question before normal
    progression continues.
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

        # Remember the remediation state before
        # recording the new response.
        return_target = (
            learner
            .remediation_return_question_id
        )

        remediation_question = (
            learner
            .remediation_question_id
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

        # ----------------------------------------------------
        # Successful remediation:
        #
        # Return to the original question before allowing
        # ordinary progression.
        # ----------------------------------------------------

        if (
            return_target is not None
            and remediation_question is not None
            and evidence.question_id
            == remediation_question
            and evidence.score >= 1.0
        ):
            learner.clear_remediation()

            return self._reassessment_decision(
                question_id=return_target
            )

        # ----------------------------------------------------
        # Learner is already inside a remediation cycle.
        #
        # If the support question was not completed
        # successfully, keep adapting inside remediation.
        # ----------------------------------------------------

        if return_target is not None:
            decision = self._selector.select(
                questions=self._questions,
                learner=learner,
            )

            if decision is None:
                return None

            learner.update_remediation_question(
                decision.question.question_id
            )

            return replace(
                decision,
                decision_type="remediate",
                return_target_question_id=(
                    return_target
                ),
                reason=(
                    "Continue remediation before "
                    "reassessing "
                    f"{return_target}. "
                    + decision.reason
                ),
            )

        # ----------------------------------------------------
        # Normal adaptive selection.
        # ----------------------------------------------------

        decision = self._selector.select(
            questions=self._questions,
            learner=learner,
        )

        if decision is None:
            return None

        # ----------------------------------------------------
        # Diagnostic remediation.
        #
        # The selector already determines whether a candidate
        # matches the learner's diagnostic evidence.
        #
        # A positive diagnostic_match means the selected
        # question provides targeted support for an observed
        # outcome/misconception.
        # ----------------------------------------------------

        if (
            evidence.score < 1.0
            and evidence.prt_outcome
            and decision.score.diagnostic_match
            > 0.0
            and decision.question.question_id
            != evidence.question_id
        ):
            learner.begin_remediation(
                return_question_id=(
                    evidence.question_id
                ),
                remediation_question_id=(
                    decision.question
                    .question_id
                ),
            )

            return replace(
                decision,
                decision_type="remediate",
                return_target_question_id=(
                    evidence.question_id
                ),
                reason=(
                    "Diagnostic evidence "
                    f"'{evidence.prt_outcome}' "
                    "triggered remediation. "
                    + decision.reason
                ),
            )

        return replace(
            decision,
            decision_type="advance",
            return_target_question_id=None,
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

    def _reassessment_decision(
        self,
        *,
        question_id: str,
    ) -> AdaptiveDecision:
        question = self._require_question(
            question_id
        )

        score = CandidateScore(
            question_id=question_id,
            total=0.0,
            difficulty_match=0.0,
            diagnostic_match=0.0,
            novelty_bonus=0.0,
            repetition_penalty=0.0,
        )

        return AdaptiveDecision(
            question=question,
            score=score,
            reason=(
                "Remediation completed. "
                "Reassess the original question "
                "before continuing."
            ),
            decision_type="reassess",
            return_target_question_id=(
                question_id
            ),
        )

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
