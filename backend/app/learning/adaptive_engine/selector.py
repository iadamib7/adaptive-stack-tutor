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

    Ordinary selection respects bank-local
    prerequisites and response-evidence mappings.

    If those relationships create a dead end after
    a response, the selector can fall back to other
    unseen questions in the same uploaded bank.
    """

    def select(
        self,
        *,
        questions: list[AdaptiveQuestion],
        learner: AdaptiveLearnerState,
    ) -> AdaptiveDecision | None:
        active_questions = [
            question
            for question in questions
            if question.active
        ]

        if not active_questions:
            return None

        if not learner.response_history:
            entry_points = [
                question
                for question in active_questions
                if question.entry_point
            ]

            candidates = (
                entry_points
                if entry_points
                else active_questions
            )

        else:
            candidates = [
                question
                for question in active_questions
                if (
                    self._prerequisites_satisfied(
                        question=question,
                        learner=learner,
                    )
                    or self._targets_current_need(
                        question=question,
                        learner=learner,
                    )
                )
            ]

            previous_question_id = (
                learner.response_history[-1].question_id
            )

            alternatives = [
                question
                for question in candidates
                if question.question_id
                != previous_question_id
            ]

            if alternatives:
                candidates = alternatives
            else:
                # Dead-end fallback:
                # if the generated graph exposes only
                # the question just answered, consider
                # unseen active questions from the same
                # uploaded bank.
                unseen = [
                    question
                    for question in active_questions
                    if (
                        question.question_id
                        != previous_question_id
                        and question.question_id
                        not in learner.seen_question_ids
                    )
                ]

                if unseen:
                    candidates = unseen

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

    @staticmethod
    def _prerequisites_satisfied(
        *,
        question: AdaptiveQuestion,
        learner: AdaptiveLearnerState,
    ) -> bool:
        return set(
            question.prerequisites
        ).issubset(
            learner.mastered_skills
        )

    @staticmethod
    def _targets_current_need(
        *,
        question: AdaptiveQuestion,
        learner: AdaptiveLearnerState,
    ) -> bool:
        if not learner.misconception_counts:
            return False

        targets = (
            set(question.supports)
            | set(question.tags)
        )

        return any(
            need in targets
            for need in learner.misconception_counts
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
                question_id=question.question_id,
                total=round(total, 6),
                difficulty_match=round(
                    difficulty_match,
                    6,
                ),
                diagnostic_match=round(
                    diagnostic_match,
                    6,
                ),
                novelty_bonus=novelty_bonus,
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

        if question.prerequisites:
            if set(
                question.prerequisites
            ).issubset(
                learner.mastered_skills
            ):
                parts.append(
                    "Its bank-local prerequisites "
                    "are currently satisfied."
                )
            elif score.diagnostic_match > 0:
                parts.append(
                    "It is eligible because it "
                    "targets current response "
                    "evidence."
                )

        if score.diagnostic_match > 0:
            parts.append(
                "The question targets previous "
                "response evidence."
            )

        if (
            question.question_id
            not in learner.seen_question_ids
        ):
            parts.append(
                "Unseen content was preferred."
            )

        return " ".join(parts)
