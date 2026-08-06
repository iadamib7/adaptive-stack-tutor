from backend.app.integrations.stack_api.adapter import (
    StackEvaluationAdapter,
)
from backend.app.learning.session.engine import (
    AdaptiveLearningSessionEngine,
)
from backend.app.learning.session.models import (
    LearningSessionState,
)


class StackAdaptiveSessionService:
    """
    Coordinate STACK evaluation with the curriculum-aware
    adaptive learning session engine.

    The service is independent of the concrete STACK client.
    Tests may use the mock client, while production can later
    use an HTTP client based on the official STACK API script.
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

    def submit_answer(
        self,
        student_id: int,
        concept_id: str,
        question_id: str,
        question_xml: str,
        student_answers: dict[str, str],
        target_prt_name: str | None = None,
        seed: int | None = None,
    ) -> LearningSessionState:
        current_session = self.session_engine.get_session(
            student_id
        )

        if current_session is None:
            raise ValueError(
                f"No active learning session exists for "
                f"student {student_id}."
            )

        if current_session.current_concept_id != concept_id:
            raise ValueError(
                "The submitted concept does not match the "
                "student's active learning session."
            )

        if current_session.question is None:
            raise ValueError(
                "The current session is not waiting for "
                "a question response."
            )

        if current_session.question.id != question_id:
            raise ValueError(
                "The submitted question does not match the "
                "question currently assigned to the student."
            )

        scored_outcome = (
            self.stack_adapter.evaluate_for_session(
                student_id=student_id,
                concept_id=concept_id,
                question_id=question_id,
                question_xml=question_xml,
                student_answers=student_answers,
                target_prt_name=target_prt_name,
                seed=seed,
            )
        )

        return self.session_engine.submit_outcome(
            scored_outcome
        )

    def get_session(
        self,
        student_id: int,
    ) -> LearningSessionState | None:
        return self.session_engine.get_session(
            student_id
        )
