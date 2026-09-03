from __future__ import annotations

from backend.app.learning.adaptive_engine.models import (
    AdaptiveDecision,
    AdaptiveLearnerState,
    AdaptiveQuestion,
    CandidateScore,
)


class DeterministicAdaptiveSelector:
    """
    Curriculum-independent deterministic selector.

    Deterministic does not mean linear:
    different learner states can produce different
    next questions, while identical states always
    produce identical decisions.
    """

    def select(
        self,
        *,
        questions: list[AdaptiveQuestion],
        learner: AdaptiveLearnerState,
    ) -> AdaptiveDecision | None:
        candidates = [
            question
            for question in questions
            if question.active
        ]

        if not candidates:
            return None

        scored = [
            self._score(
                question=question,
                learner=learner,
            )
            for question in candidates
        ]

        scored.sort(
            key=lambda item: (
                -item[1].total,
                item[0].question_id,
            )
        )

        question, score = scored[0]

        return AdaptiveDecision(
            question=question,
            score=score,
            reason=self._reason(
                question=question,
                learner=learner,
                score=score,
            ),
        )

    def _score(
        self,
        *,
        question: AdaptiveQuestion,
        learner: AdaptiveLearnerState,
    ) -> tuple[
        AdaptiveQuestion,
        CandidateScore,
    ]:
        difference = abs(
            question.difficulty
            - learner.ability
        )

        difficulty_match = max(
            0.0,
            3.0 - difference,
        )

        diagnostic_match = 0.0

        for need, count in (
            learner.misconception_counts.items()
        ):
            if (
                need in question.supports
                or need in question.tags
            ):
                diagnostic_match += (
                    2.0 * count
                )

        novelty_bonus = (
            1.5
            if question.question_id
            not in learner.seen_question_ids
            else 0.0
        )

        attempts = (
            learner.attempts_by_question.get(
                question.question_id,
                0,
            )
        )

        repetition_penalty = (
            float(attempts) * 2.0
        )

        total = (
            difficulty_match
            + diagnostic_match
            + novelty_bonus
            - repetition_penalty
        )

        return (
            question,
            CandidateScore(
                question_id=(
                    question.question_id
                ),
                total=round(
                    total,
                    6,
                ),
                difficulty_match=round(
                    difficulty_match,
                    6,
                ),
                diagnostic_match=round(
                    diagnostic_match,
                    6,
                ),
                novelty_bonus=(
                    novelty_bonus
                ),
                repetition_penalty=(
                    repetition_penalty
                ),
            ),
        )

    @staticmethod
    def _reason(
        *,
        question: AdaptiveQuestion,
        learner: AdaptiveLearnerState,
        score: CandidateScore,
    ) -> str:
        parts = [
            (
                "Selected deterministically from "
                "the available question bank."
            ),
            (
                "Difficulty suitability="
                f"{score.difficulty_match:.2f}."
            ),
        ]

        if score.diagnostic_match > 0:
            parts.append(
                "The question also targets "
                "previous response evidence."
            )

        if (
            question.question_id
            not in learner.seen_question_ids
        ):
            parts.append(
                "Unseen content was preferred."
            )

        return " ".join(parts)
