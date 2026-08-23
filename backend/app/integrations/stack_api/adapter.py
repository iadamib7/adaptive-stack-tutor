from __future__ import annotations

from backend.app.integrations.stack_api.client import (
    StackEvaluationClient,
)
from backend.app.integrations.stack_api.models import (
    NormalizedStackResult,
    StackEvaluationRequest,
    StackPRTResult,
)
from backend.app.learning.session.models import (
    ScoredStackOutcome,
)


class StackEvaluationAdapter:
    """
    Convert STACK results into one adaptive session outcome.

    A learner task may depend on one or several STACK PRTs.
    """

    def __init__(
        self,
        client: StackEvaluationClient,
    ) -> None:
        self.client = client

    def evaluate_for_session(
        self,
        student_id: int,
        concept_id: str,
        question_id: str,
        question_xml: str,
        student_answers: dict[str, str],
        target_prt_name: str | None = None,
        target_prt_names: list[str] | None = None,
        seed: int | None = None,
    ) -> ScoredStackOutcome:
        request = StackEvaluationRequest(
            question_id=question_id,
            question_xml=question_xml,
            student_answers=student_answers,
            seed=seed,
        )

        result = self.client.evaluate(
            request
        )

        return self.to_session_outcome(
            student_id=student_id,
            concept_id=concept_id,
            result=result,
            target_prt_name=target_prt_name,
            target_prt_names=target_prt_names,
        )

    def to_session_outcome(
        self,
        student_id: int,
        concept_id: str,
        result: NormalizedStackResult,
        target_prt_name: str | None = None,
        target_prt_names: list[str] | None = None,
    ) -> ScoredStackOutcome:
        if not result.valid:
            error_message = (
                self._build_error_message(
                    result
                )
            )

            raise ValueError(
                "STACK could not validate the learner "
                f"response. {error_message}"
            )

        selected_prts = self._select_prts(
            result=result,
            target_prt_name=target_prt_name,
            target_prt_names=target_prt_names,
        )

        score = self._aggregate_score(
            selected_prts
        )

        outcome_code = (
            self._build_outcome_code(
                selected_prts
            )
        )

        feedback = self._combine_feedback(
            result=result,
            selected_prts=selected_prts,
        )

        return ScoredStackOutcome(
            student_id=student_id,
            concept_id=concept_id,
            question_id=result.question_id,
            outcome_code=outcome_code,
            score=score,
            stack_feedback=feedback,
        )

    @staticmethod
    def _select_prts(
        *,
        result: NormalizedStackResult,
        target_prt_name: str | None,
        target_prt_names: list[str] | None,
    ) -> list[StackPRTResult]:
        if not result.prts:
            raise ValueError(
                "STACK returned no PRT results."
            )

        requested_many = [
            name
            for name in (
                target_prt_names or []
            )
            if name
        ]

        if (
            target_prt_name is not None
            and requested_many
        ):
            raise ValueError(
                "Specify either target_prt_name or "
                "target_prt_names, not both."
            )

        if requested_many:
            unique_names: list[str] = []

            for name in requested_many:
                if name not in unique_names:
                    unique_names.append(
                        name
                    )

            available = {
                prt.prt_name: prt
                for prt in result.prts
            }

            missing = [
                name
                for name in unique_names
                if name not in available
            ]

            if missing:
                raise ValueError(
                    "STACK result does not contain PRT "
                    + ", ".join(missing)
                    + "."
                )

            return [
                available[name]
                for name in unique_names
            ]

        if target_prt_name is not None:
            for prt in result.prts:
                if (
                    prt.prt_name
                    == target_prt_name
                ):
                    return [prt]

            raise ValueError(
                "STACK result does not contain PRT "
                f"{target_prt_name}."
            )

        if len(result.prts) > 1:
            raise ValueError(
                "STACK returned multiple PRT results. "
                "A target PRT name or target PRT names "
                "must be provided."
            )

        return [
            result.prts[0]
        ]

    @classmethod
    def _aggregate_score(
        cls,
        prts: list[StackPRTResult],
    ) -> float:
        scores = [
            cls._normalize_score(
                prt.score
            )
            for prt in prts
        ]

        return sum(scores) / len(scores)

    @classmethod
    def _build_outcome_code(
        cls,
        prts: list[StackPRTResult],
    ) -> str:
        notes = [
            cls._select_answer_note(
                prt
            )
            for prt in prts
        ]

        if len(notes) == 1:
            return notes[0]

        return (
            "adaptive-task:"
            + "|".join(notes)
        )

    @staticmethod
    def _select_answer_note(
        prt: StackPRTResult,
    ) -> str:
        if not prt.answer_notes:
            raise ValueError(
                f"STACK PRT {prt.prt_name} returned "
                "no answer note."
            )

        return prt.answer_notes[-1]

    @staticmethod
    def _normalize_score(
        score: float,
    ) -> float:
        return max(
            0.0,
            min(score, 1.0),
        )

    @staticmethod
    def _combine_feedback(
        *,
        result: NormalizedStackResult,
        selected_prts: list[StackPRTResult],
    ) -> str | None:
        feedback_parts: list[str] = []

        for prt in selected_prts:
            feedback = prt.feedback

            if (
                feedback
                and feedback.strip()
                and feedback.strip()
                not in feedback_parts
            ):
                feedback_parts.append(
                    feedback.strip()
                )

        if (
            result.raw_feedback
            and result.raw_feedback.strip()
            and result.raw_feedback.strip()
            not in feedback_parts
        ):
            feedback_parts.append(
                result.raw_feedback.strip()
            )

        if not feedback_parts:
            return None

        return " ".join(
            feedback_parts
        )

    @staticmethod
    def _build_error_message(
        result: NormalizedStackResult,
    ) -> str:
        errors = result.errors

        if not errors:
            return (
                "No additional validation details were "
                "returned."
            )

        return " ".join(errors)
