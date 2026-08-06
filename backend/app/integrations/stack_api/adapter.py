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
    Convert STACK evaluation results into the internal outcome
    consumed by the adaptive learning session engine.
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
        seed: int | None = None,
    ) -> ScoredStackOutcome:
        request = StackEvaluationRequest(
            question_id=question_id,
            question_xml=question_xml,
            student_answers=student_answers,
            seed=seed,
        )

        result = self.client.evaluate(request)

        return self.to_session_outcome(
            student_id=student_id,
            concept_id=concept_id,
            result=result,
            target_prt_name=target_prt_name,
        )

    def to_session_outcome(
        self,
        student_id: int,
        concept_id: str,
        result: NormalizedStackResult,
        target_prt_name: str | None = None,
    ) -> ScoredStackOutcome:
        if not result.valid:
            error_message = self._build_error_message(
                result
            )

            raise ValueError(
                "STACK could not validate the learner "
                f"response. {error_message}"
            )

        selected_prt = self._select_prt(
            result=result,
            target_prt_name=target_prt_name,
        )

        outcome_code = self._select_answer_note(
            selected_prt
        )

        feedback = self._combine_feedback(
            result=result,
            selected_prt=selected_prt,
        )

        normalized_score = self._normalize_score(
            selected_prt.score
        )

        return ScoredStackOutcome(
            student_id=student_id,
            concept_id=concept_id,
            question_id=result.question_id,
            outcome_code=outcome_code,
            score=normalized_score,
            stack_feedback=feedback,
        )

    @staticmethod
    def _select_prt(
        result: NormalizedStackResult,
        target_prt_name: str | None,
    ) -> StackPRTResult:
        if not result.prts:
            raise ValueError(
                "STACK returned no PRT results."
            )

        if target_prt_name is None:
            if len(result.prts) > 1:
                raise ValueError(
                    "STACK returned multiple PRT results. "
                    "A target PRT name must be provided."
                )

            return result.prts[0]

        for prt in result.prts:
            if prt.prt_name == target_prt_name:
                return prt

        raise ValueError(
            f"STACK result does not contain PRT "
            f"{target_prt_name}."
        )

    @staticmethod
    def _select_answer_note(
        prt: StackPRTResult,
    ) -> str:
        if not prt.answer_notes:
            raise ValueError(
                f"STACK PRT {prt.prt_name} returned no "
                "answer note."
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
        result: NormalizedStackResult,
        selected_prt: StackPRTResult,
    ) -> str | None:
        feedback_parts = [
            feedback.strip()
            for feedback in [
                selected_prt.feedback,
                result.raw_feedback,
            ]
            if feedback and feedback.strip()
        ]

        if not feedback_parts:
            return None

        return " ".join(feedback_parts)

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
