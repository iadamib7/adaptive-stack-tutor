from backend.app.integrations.stack_api.adapter import (
    StackEvaluationAdapter,
)
from backend.app.learning.session.engine import (
    AdaptiveLearningSessionEngine,
)
from backend.app.learning.session.models import (
    LearningSessionState,
    ScoredStackOutcome,
)


class StackAdaptiveSessionService:
    """
    Coordinate STACK evaluation with the curriculum-aware
    adaptive learning session engine.

    Evaluation and curriculum progression are intentionally
    separate so adaptive sub-tasks can be graded without
    prematurely completing their source STACK question.
    """

    def __init__(
        self,
        stack_adapter: StackEvaluationAdapter,
        session_engine: AdaptiveLearningSessionEngine,
    ) -> None:
        self.stack_adapter = stack_adapter
        self.session_engine = session_engine

    def start_session(
        self,
        student_id: int,
        concept_id: str,
    ) -> LearningSessionState:
        return self.session_engine.start_session(
            student_id=student_id,
            concept_id=concept_id,
        )

    def evaluate_answer(
        self,
        *,
        student_id: int,
        concept_id: str,
        question_id: str,
        question_xml: str,
        student_answers: dict[str, str],
        target_prt_name: str | None = None,
        target_prt_names: list[str] | None = None,
        seed: int | None = None,
    ) -> ScoredStackOutcome:
        self._validate_submission_context(
            student_id=student_id,
            concept_id=concept_id,
            question_id=question_id,
        )

        return self.stack_adapter.evaluate_for_session(
            student_id=student_id,
            concept_id=concept_id,
            question_id=question_id,
            question_xml=question_xml,
            student_answers=student_answers,
            target_prt_name=target_prt_name,
            target_prt_names=target_prt_names,
            seed=seed,
        )

    def submit_outcome(
        self,
        outcome: ScoredStackOutcome,
    ) -> LearningSessionState:
        return self.session_engine.submit_outcome(
            outcome
        )

    def submit_answer(
        self,
        student_id: int,
        concept_id: str,
        question_id: str,
        question_xml: str,
        student_answers: dict[str, str],
        target_prt_name: str | None = None,
        target_prt_names: list[str] | None = None,
        seed: int | None = None,
    ) -> LearningSessionState:
        """
        Backward-compatible full-question submission.

        Existing callers still evaluate and immediately submit
        the resulting evidence to the curriculum engine.
        """

        scored_outcome = self.evaluate_answer(
            student_id=student_id,
            concept_id=concept_id,
            question_id=question_id,
            question_xml=question_xml,
            student_answers=student_answers,
            target_prt_name=target_prt_name,
            target_prt_names=target_prt_names,
            seed=seed,
        )

        return self.submit_outcome(
            scored_outcome
        )

    def get_session(
        self,
        student_id: int,
    ) -> LearningSessionState | None:
        return self.session_engine.get_session(
            student_id
        )

    def _validate_submission_context(
        self,
        *,
        student_id: int,
        concept_id: str,
        question_id: str,
    ) -> None:
        current_session = (
            self.session_engine.get_session(
                student_id
            )
        )

        if current_session is None:
            raise ValueError(
                f"No active learning session exists for "
                f"student {student_id}."
            )

        if (
            current_session.current_concept_id
            != concept_id
        ):
            raise ValueError(
                "The submitted concept does not match the "
                "student's active learning session."
            )

        if current_session.question is None:
            raise ValueError(
                "The current session is not waiting for "
                "a question response."
            )

        if (
            current_session.question.id
            != question_id
        ):
            raise ValueError(
                "The submitted question does not match the "
                "question currently assigned to the student."
            )
